import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed } from '@ton/crypto';
import { Address, toNano, beginCell, SendMode, TupleItem, internal } from '@ton/core';
import * as fs from 'fs';

const SESSION_FILE = 'session.json';
function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
    const s = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
    console.log(`UUID: ${s.uuid}`);
    const client = new TonClient({ endpoint: s.api.replace(/\/+$/, '') + '/jsonRPC', timeout: 30000 });
    const challengeAddr = Address.parse(s.challenge);
    const kp = keyPairFromSeed(Buffer.from(s.seed, 'hex'));
    const wallet = WalletContractV3R2.create({ workchain: -1, publicKey: kp.publicKey, walletId: s.wallet_id });
    const openedWallet = client.open(wallet);
    const provider = client.provider(wallet.address, wallet.init);

    const mr = await client.runMethod(challengeAddr, 'minter');
    const minter = mr.stack.readAddress();
    const pwc = beginCell().storeAddress(wallet.address).endCell();
    const pwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: pwc } as TupleItem]);
    const pJetton = pwr.stack.readAddress();
    const cwc = beginCell().storeAddress(challengeAddr).endCell();
    const cwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: cwc } as TupleItem]);
    const cJetton = cwr.stack.readAddress();

    // Check raw account data
    console.log(`\n=== Checking cJetton account ===`);
    try {
        const info = await client.getAccountLite(cJetton);
        console.log(`  Account state: ${info?.accountState?.type}`);
        if (info?.accountState?.type === 'active') {
            const data = info.accountState.storage?.data;
            console.log(`  Data hash: ${data?.hash().toString('hex').slice(0, 20)}`);
            console.log(`  Balance: ${info.accountState.storage?.balance?.toString() || 'unknown'}`);
        } else if (info?.accountState?.type === 'uninitialized') {
            console.log(`  Account exists but uninitialized (no jettons)`);
        } else if (info?.accountState?.type === 'nonexist') {
            console.log(`  Account doesn't exist at all`);
        }
    } catch (e: any) { console.log(`  Error: ${e.message.slice(0, 80)}`); }

    // Check challenge account raw data
    console.log(`\n=== Checking challenge raw data ===`);
    try {
        const { Cell } = await import('@ton/core');
        const info = await client.getAccountLite(challengeAddr);
        console.log(`  Account state: ${info?.accountState?.type}`);
        if (info?.accountState?.type === 'active') {
            const data = info.accountState.storage?.data;
            console.log(`  Data hash: ${data?.hash().toString('hex').slice(0, 20)}`);
            if (data) {
                const cs = data.beginParse();
                const bonus = cs.loadUint(8);
                const player = cs.loadAddress();
                const hasMinter = cs.loadBit();
                const minterAddr = hasMinter ? cs.loadAddress() : null;
                const hasWallet = cs.loadBit();
                const walletAddr = hasWallet ? cs.loadAddress() : null;
                const solved = cs.loadBit();
                console.log(`  remainingPlayerBonus: ${bonus}`);
                console.log(`  player: ${player}`);
                console.log(`  minter: ${hasMinter ? minterAddr : 'null'}`);
                console.log(`  wallet: ${hasWallet ? walletAddr : 'null'}`);
                console.log(`  isSolved: ${solved}`);
            }
        }
    } catch (e: any) { console.log(`  Error: ${e.message.slice(0, 80)}`); }

    // Check pJetton and cJetton directly
    console.log(`\n=== Checking pJetton get_wallet_data ===`);
    try {
        const wd = await client.runMethod(pJetton, 'get_wallet_data');
        const bal = wd.stack.readBigNumber();
        const owner = wd.stack.readAddress();
        const minterAddr = wd.stack.readAddress();
        const code = wd.stack.readCell();
        console.log(`  Balance: ${bal}, Owner: ${owner.toString().slice(0, 30)}..., Minter: ${minterAddr.toString().slice(0, 30)}...`);
    } catch (e: any) { console.log(`  Error: ${e.message.slice(0, 80)}`); }

    console.log(`\n=== Checking cJetton get_wallet_data ===`);
    try {
        const wd = await client.runMethod(cJetton, 'get_wallet_data');
        const bal = wd.stack.readBigNumber();
        const owner = wd.stack.readAddress();
        const minterAddr = wd.stack.readAddress();
        const code = wd.stack.readCell();
        console.log(`  Balance: ${bal}, Owner: ${owner.toString().slice(0, 30)}..., Minter: ${minterAddr.toString().slice(0, 30)}...`);
    } catch (e: any) { console.log(`  Error: ${e.message.slice(0, 80)}`); }

    // Claim bonus and re-check
    console.log(`\n=== Claiming PlayerBonus ===`);
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
    let seqno = await wallet.getSeqno(provider);
    await openedWallet.sendTransfer({ seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano('0.3'), body: bonusBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) break; }
    await sleep(15000);

    // Re-check everything after bonus
    console.log(`\n=== After PlayerBonus ===`);
    console.log(`pJetton: ${await getJettonBal(client, pJetton)}`);
    console.log(`cJetton: ${await getJettonBal(client, cJetton)}`);

    // Check challenge data again
    const info2 = await client.getAccountLite(challengeAddr);
    if (info2?.accountState?.type === 'active') {
        const cs2 = info2.accountState.storage.data.beginParse();
        const bonus2 = cs2.loadUint(8);
        cs2.loadAddress(); // player
        cs2.loadBit();
        cs2.skipAddress();
        const hasWallet2 = cs2.loadBit();
        const walletAddr2 = hasWallet2 ? cs2.loadAddress() : null;
        console.log(`remainingPlayerBonus: ${bonus2}, wallet: ${hasWallet2 ? walletAddr2.toString().slice(0,30) : 'null'}`);
    }

    console.log(`\n=== Done ===`);
}

async function getJettonBal(client: TonClient, addr: Address): Promise<bigint | null> {
    try { const r = await client.runMethod(addr, 'get_wallet_data'); return r.stack.readBigNumber(); } catch { return null; }
}

main().catch(console.error);
