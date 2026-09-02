import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed } from '@ton/crypto';
import { Address, toNano, beginCell, Cell, SendMode, TupleItem, internal } from '@ton/core';
import * as fs from 'fs';

const SESSION_FILE = 'session.json';
function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

async function readChallengeStorage(client: TonClient, addr: Address) {
    const acc = await client.getAccount(addr);
    if (acc.account?.type !== 'active' || !acc.account.storage.data) {
        console.log(`  Account not active`);
        return null;
    }
    const data = acc.account.storage.data;
    const cs = data.beginParse();
    const remainingBonus = cs.loadUint(8);
    const player = cs.loadAddress();
    const hasMinter = cs.loadBit();
    const minterAddr = hasMinter ? cs.loadAddress() : null;
    const hasWallet = cs.loadBit();
    const walletAddr = hasWallet ? cs.loadAddress() : null;
    const solved = cs.loadBit();
    return { remainingBonus, player, hasMinter, minterAddr, hasWallet, walletAddr, solved, balance: Number(acc.account.storage.balance) / 1e9 };
}

async function main() {
    const s = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
    console.log(`UUID: ${s.uuid}`);
    const client = new TonClient({ endpoint: s.api.replace(/\/+$/, '') + '/jsonRPC', timeout: 30000 });
    const challengeAddr = Address.parse(s.challenge);
    const kp = keyPairFromSeed(Buffer.from(s.seed, 'hex'));
    const wallet = WalletContractV3R2.create({ workchain: -1, publicKey: kp.publicKey, walletId: s.wallet_id });
    const openedWallet = client.open(wallet);
    const provider = client.provider(wallet.address, wallet.init);
    console.log(`Wallet: ${wallet.address}`);

    const mr = await client.runMethod(challengeAddr, 'minter');
    const minter = mr.stack.readAddress();
    const pwc = beginCell().storeAddress(wallet.address).endCell();
    const pwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: pwc } as TupleItem]);
    const pJetton = pwr.stack.readAddress();
    const cwc = beginCell().storeAddress(challengeAddr).endCell();
    const cwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: cwc } as TupleItem]);
    const cJetton = cwr.stack.readAddress();
    console.log(`cJetton: ${cJetton}`);

    // Read initial storage
    console.log(`\n=== Initial Challenge Storage ===`);
    let st = await readChallengeStorage(client, challengeAddr);
    if (st) {
        console.log(`  remainingPlayerBonus: ${st.remainingBonus}`);
        console.log(`  player: ${st.player.toString().slice(0, 40)}...`);
        console.log(`  minter: ${st.hasMinter ? st.minterAddr?.toString().slice(0, 30) : 'null'}`);
        console.log(`  wallet: ${st.hasWallet ? st.walletAddr?.toString().slice(0, 50) : 'null'}`);
        console.log(`  wallet MATCHES cJetton: ${st.hasWallet && st.walletAddr?.toString() === cJetton.toString()}`);
        console.log(`  isSolved: ${st.solved}`);
        console.log(`  Balance: ${st.balance} TON`);
    }

    // Check cJetton before bonus
    console.log(`\n=== cJetton before bonus ===`);
    try {
        const r = await client.runMethod(cJetton, 'get_wallet_data');
        console.log(`  Balance: ${r.stack.readBigNumber()}`);
    } catch (e: any) {
        const code = e.response?.data?.error?.message || e.message.slice(0, 80);
        console.log(`  Status: ${code}`);
    }

    // Claim PlayerBonus
    console.log(`\n=== Claiming PlayerBonus ===`);
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
    let seqno = await wallet.getSeqno(provider);
    console.log(`  seqno=${seqno}, TON=${Number(await client.getBalance(wallet.address))/1e9}`);
    await openedWallet.sendTransfer({ seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano('0.35'), body: bonusBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) break; }
    await sleep(15000);

    // Check storage after bonus
    st = await readChallengeStorage(client, challengeAddr);
    if (st) {
        console.log(`\n=== After Bonus Storage ===`);
        console.log(`  remainingPlayerBonus: ${st.remainingBonus}`);
        console.log(`  wallet: ${st.hasWallet ? st.walletAddr?.toString().slice(0, 50) : 'null'}`);
        console.log(`  wallet MATCHES cJetton: ${st.hasWallet && st.walletAddr?.toString() === cJetton.toString()}`);
        console.log(`  isSolved: ${st.solved}`);
        console.log(`  Balance: ${st.balance} TON`);
    }

    // Check pJetton and cJetton
    console.log(`\n=== After Bonus Balances ===`);
    try { const r = await client.runMethod(pJetton, 'get_wallet_data'); console.log(`  pJetton: ${r.stack.readBigNumber()}`); }
    catch (e: any) { console.log(`  pJetton: ERROR`); }
    try { const r = await client.runMethod(cJetton, 'get_wallet_data'); console.log(`  cJetton: ${r.stack.readBigNumber()}`); }
    catch (e: any) { console.log(`  cJetton: NOT DEPLOYED`); }

    console.log(`\n=== Done ===`);
}
main().catch(console.error);
