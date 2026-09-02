import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed } from '@ton/crypto';
import { Address, toNano, beginCell, SendMode, TupleItem, internal } from '@ton/core';
import * as fs from 'fs';

const SESSION_FILE = 'session.json';
async function main() {
    const s = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
    const client = new TonClient({ endpoint: s.api.replace(/\/+$/, '') + '/jsonRPC', timeout: 30000 });
    const challengeAddr = Address.parse(s.challenge);
    const kp = keyPairFromSeed(Buffer.from(s.seed, 'hex'));
    const wallet = WalletContractV3R2.create({ workchain: -1, publicKey: kp.publicKey, walletId: s.wallet_id });
    const openedWallet = client.open(wallet);
    const provider = client.provider(wallet.address, wallet.init);

    // Get addresses
    const mr = await client.runMethod(challengeAddr, 'minter');
    const minter = mr.stack.readAddress();
    const cwc = beginCell().storeAddress(challengeAddr).endCell();
    const cwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: cwc } as TupleItem]);
    const cJetton = cwr.stack.readAddress();
    const pwc = beginCell().storeAddress(wallet.address).endCell();
    const pwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: pwc } as TupleItem]);
    const pJetton = pwr.stack.readAddress();

    console.log(`Wallet: ${wallet.address}`);
    console.log(`Challenge: ${challengeAddr}`);
    console.log(`Minter: ${minter}`);
    console.log(`pJetton: ${pJetton}`);
    console.log(`cJetton: ${cJetton}`);

    // Check initial state
    console.log(`\n=== Initial State ===`);
    console.log(`Wallet TON: ${Number(await client.getBalance(wallet.address))/1e9}`);

    // Try to check cJetton account state via getAddressInformation
    const resp = await client.getAccountLite(cJetton);
    console.log(`cJetton account state before: ${resp?.accountState?.type || 'nonexistent'}`);
    if (resp?.accountState?.type === 'active') {
        const data = resp.accountState.storage?.data;
        console.log(`  Data available: ${!!data}, data hash: ${data ? data.hash().toString('hex').slice(0, 16) : 'none'}`);
    }

    // Check pJetton data
    console.log(`\npJetton get_wallet_data:`);
    try {
        const pw = await client.runMethod(pJetton, 'get_wallet_data');
        const bal = pw.stack.readBigNumber();
        const owner = pw.stack.readAddress();
        const minterAddr = pw.stack.readAddress();
        const codeCell = pw.stack.readCell();
        console.log(`  Balance: ${bal}`);
        console.log(`  Owner: ${owner}`);
        console.log(`  Minter: ${minterAddr}`);
        console.log(`  Code hash: ${codeCell.hash().toString('hex').slice(0, 16)}...`);
    } catch (e: any) { console.log(`  Error: ${e.message.slice(0, 100)}`); }

    // Claim bonus
    console.log(`\n=== Claiming Bonus ===`);
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
    let seqno = await wallet.getSeqno(provider);
    await openedWallet.sendTransfer({ seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano('0.35'), body: bonusBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) break; }
    await sleep(10000);
    console.log(`After bonus: Jetton=${await getJettonBal(client, pJetton)} TON=${Number(await client.getBalance(wallet.address))/1e9}`);

    // Now check cJetton address more carefully
    console.log(`\n=== Debating cJetton address ===`);
    // computeJettonWalletAddress function in @ton/ton
    // Try computing address using the minter's `get_wallet_address` get method
    console.log(`cJetton from get_wallet_address: ${cJetton}`);

    // Also compute using pJetton's code cell
    console.log(`\n=== Alternative: compute from minter code ===`);
    const jd = await client.runMethod(minter, 'get_jetton_data');
    const supply = jd.stack.readBigNumber();
    const mintable = jd.stack.readBoolean();
    const admin = jd.stack.readAddress();
    jd.stack.readCell(); // content
    const jettonWalletCode = jd.stack.readCell(); // jettonWalletCode
    console.log(`Minter supply: ${supply}`);
    console.log(`Admin (challenge): ${admin}`);

    console.log(`\nChecking admin == challenge? ${admin.toString() === challengeAddr.toString()}`);

    // Compute cJetton address from code + data
    const { beginCell } = await import('@ton/core');
    const walletData = beginCell()
        .storeCoins(0n) // balance
        .storeAddress(challengeAddr) // owner
        .storeAddress(minter) // minter
        .endCell();
    const walletStateInit = { code: jettonWalletCode, data: walletData };
    const { Contract } = await import('@ton/ton');

    // Actually just compute the address hash
    const computedAddr = new Address(0, walletStateInit.data.hash());
    console.log(`Computed address (from data hash): ${computedAddr}`);

    // Use state init to compute address properly
    const cAddr = await computeAddress({ code: jettonWalletCode, data: walletData });
    console.log(`Computed cJetton via state init: ${cAddr}`);
    console.log(`cJetton from get_wallet_address: ${cJetton}`);
    console.log(`Match: ${cAddr.toString() === cJetton.toString()}`);

    // Now run isSolved
    try {
        const r = await client.runMethod(challengeAddr, 'isSolved');
        console.log(`\nisSolved: ${r.stack.readBoolean()}`);
    } catch (e: any) { console.log(`\nisSolved error: ${e.message.slice(0, 100)}`); }
}

async function computeAddress(stateInit: any) {
    // Compute contract address from state init
    const { Builder, Cell } = await import('@ton/core');
    const hash = (new Builder().store(stateInit)).endCell().hash();
    return Address.parseRaw(`0:${hash.toString('hex')}`);
}

function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

async function getJettonBal(client: TonClient, addr: Address): Promise<bigint | null> {
    try { const r = await client.runMethod(addr, 'get_wallet_data'); return r.stack.readBigNumber(); } catch { return null; }
}

main().catch(console.error);
