import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed } from '@ton/crypto';
import { Address, toNano, beginCell, Cell, SendMode, TupleItem, internal } from '@ton/core';
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
    const cwc = beginCell().storeAddress(challengeAddr).endCell();
    const cwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: cwc } as TupleItem]);
    const cJetton = cwr.stack.readAddress();

    // Read challenge storage via getAccount
    console.log(`\n=== Challenge storage via getAccount ===`);
    try {
        const acc = await client.getAccount(challengeAddr);
        console.log(`  Acc type: ${acc.account?.type}`);
        if (acc.account?.type === 'active') {
            const data = acc.account.storage.data;
            console.log(`  Data hash: ${data?.hash().toString('hex').slice(0, 20)}`);
            console.log(`  Balance: ${Number(acc.account.storage.balance) / 1e9} TON`);
            if (data) {
                const cs = data.beginParse();
                const remainingBonus = cs.loadUint(8);
                const player = cs.loadAddress();
                const hasMinter = cs.loadBit();
                const minterAddr = hasMinter ? cs.loadAddress() : null;
                const hasWallet = cs.loadBit();
                const walletAddr = hasWallet ? cs.loadAddress() : null;
                const solved = cs.loadBit();
                console.log(`  remainingPlayerBonus: ${remainingBonus}`);
                console.log(`  player: ${player}`);
                console.log(`  minter: ${hasMinter ? minterAddr?.toString().slice(0,30) : 'null'}`);
                console.log(`  wallet: ${hasWallet ? walletAddr?.toString().slice(0,50) : 'null'}`);
                console.log(`  isSolved: ${solved}`);

                if (hasWallet && walletAddr) {
                    console.log(`\n  ✅ wallet IS set: ${walletAddr}`);
                    console.log(`  cJetton from get_wallet_address: ${cJetton}`);
                    console.log(`  Match: ${walletAddr.toString() === cJetton.toString()}`);
                } else {
                    console.log(`\n  ❌ wallet is NULL — SetupChallenge wallet request failed!`);
                }
            }
        }
    } catch (e: any) { console.log(`  getAccount error: ${e.message.slice(0, 120)}`); }

    // Claim bonus
    console.log(`\n=== Claiming PlayerBonus ===`);
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
    let seqno = await wallet.getSeqno(provider);
    await openedWallet.sendTransfer({ seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano('0.3'), body: bonusBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) break; }
    await sleep(15000);

    // Re-check storage
    console.log(`\n=== After bonus storage ===`);
    try {
        const acc = await client.getAccount(challengeAddr);
        const data = acc.account?.storage.data;
        if (data) {
            const cs = data.beginParse();
            const remainingBonus = cs.loadUint(8);
            const player = cs.loadAddress();
            cs.loadBit(); const m = cs.loadAddress(); console.log(`  player: ${player}`);
            const hasWallet = cs.loadBit();
            const walletAddr = hasWallet ? cs.loadAddress() : null;
            console.log(`  remainingPlayerBonus: ${remainingBonus}`);
            console.log(`  wallet: ${hasWallet ? walletAddr?.toString().slice(0,50) : 'null'}`);
        }
    } catch (e: any) { console.log(`  Error: ${e.message.slice(0, 120)}`); }

    console.log(`\n=== Done ===`);
}
main().catch(console.error);
