import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed } from '@ton/crypto';
import { Address, toNano, beginCell, SendMode, TupleItem, internal } from '@ton/core';
import * as fs from 'fs';

const SESSION_FILE = 'session.json';
interface SessionData { uuid: string; challenge: string; api: string; wallet_id: number; seed: string; }
function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

async function getBal(client: TonClient, addr: Address) { return client.getBalance(addr); }
async function getJettonBal(client: TonClient, addr: Address) {
    try { const r = await client.runMethod(addr, 'get_wallet_data'); return r.stack.readBigNumber(); } catch { return null; }
}

async function sendMsg(openedWallet: any, wallet: any, provider: any, kp: any, to: Address, value: bigint, body: any) {
    const seqno = await wallet.getSeqno(provider);
    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to, value, body, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) return; }
    throw new Error(`seqno stuck`);
}

async function main() {
    const s: SessionData = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
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

    // Initial state
    let ton = await getBal(client, wallet.address);
    let jet = await getJettonBal(client, pJetton);
    let challBal = await getBal(client, challengeAddr);
    let cJetBal = await getJettonBal(client, cJetton);
    console.log(`Init: TON=${Number(ton)/1e9} Jetton=${jet} Chall=${Number(challBal)/1e9} cJetton=${cJetBal}`);

    // Claim PlayerBonus
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
    await sendMsg(openedWallet, wallet, provider, kp, challengeAddr, toNano('0.3'), bonusBody);
    await sleep(15000);
    ton = await getBal(client, wallet.address);
    jet = await getJettonBal(client, pJetton);
    challBal = await getBal(client, challengeAddr);
    cJetBal = await getJettonBal(client, cJetton);
    console.log(`After Bonus: TON=${Number(ton)/1e9} Jetton=${jet} Chall=${Number(challBal)/1e9} cJetton=${cJetBal}`);

    if (jet === null || jet < 1n) { console.log(`No jettons`); return; }

    // Now send 1 jetton to cJetton with Sell forward payload
    // Keep TON value within our budget (~0.2 TON)
    const forwardTon = toNano('0.05'); // standard forward ton amount
    const sellBody = beginCell()
        .storeUint(0x0f8a7ea5, 32).storeUint(0, 64)
        .storeCoins(1n).storeAddress(cJetton).storeAddress(null)
        .storeBit(0).storeCoins(forwardTon)
        .storeUint(0x13370004, 32).storeUint(0, 64) // Sell op
    .endCell();

    const tonBefore = await getBal(client, wallet.address);
    console.log(`\nSending 1 jetton + Sell, forwardTon=${Number(forwardTon)/1e9} TON...`);
    console.log(`TON before: ${Number(tonBefore)/1e9} (sending ${Number(toNano('0.18'))/1e9} TON to jetton wallet)`);

    try {
        await sendMsg(openedWallet, wallet, provider, kp, pJetton, toNano('0.18'), sellBody);
        await sleep(20000);
    } catch (e: any) { console.log(`Error: ${e.message.slice(0,100)}`); }

    const tonAfter = await getBal(client, wallet.address);
    jet = await getJettonBal(client, pJetton);
    challBal = await getBal(client, challengeAddr);
    cJetBal = await getJettonBal(client, cJetton);
    const diff = Number(tonAfter - tonBefore) / 1e9;
    console.log(`\nAfter Sell:`);
    console.log(`  TON: ${Number(tonBefore)/1e9} → ${Number(tonAfter)/1e9} (diff: ${diff.toFixed(4)})`);
    console.log(`  Jetton: ${jet}`);
    console.log(`  Chall: ${Number(challBal)/1e9}`);
    console.log(`  cJetton: ${cJetBal}`);

    if (diff > 0.5) {
        console.log(`\n✅ SELL PAID ~${diff.toFixed(2)} TON (TOKEN_PRICE works!)`);
    } else {
        console.log(`\n⚠️  Sell paid only ~${diff.toFixed(4)} TON (mode 64 overrides value)`);
    }

    // Also test isSolved
    for (let i = 0; i < 5; i++) {
        try { const r = await client.runMethod(challengeAddr, 'isSolved'); const ok = r.stack.readBoolean(); if (ok) { console.log(`\n🎉 SOLVED!`); process.exit(0); } console.log(`  isSolved check ${i+1}: false`); } catch {}
        await sleep(3000);
    }
}
main().catch(console.error);
