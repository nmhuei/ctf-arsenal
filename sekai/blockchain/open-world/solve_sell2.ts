import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed } from '@ton/crypto';
import { Address, toNano, beginCell, SendMode, TupleItem, internal } from '@ton/core';
import * as fs from 'fs';

const SESSION_FILE = 'session.json';
function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

async function getBal(client: TonClient, addr: Address) { return client.getBalance(addr); }
async function getJettonBal(client: TonClient, addr: Address): Promise<bigint | null> {
    try { const r = await client.runMethod(addr, 'get_wallet_data'); return r.stack.readBigNumber(); } catch { return null; }
}

async function main() {
    const s = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
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

    // Claim PlayerBonus
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
    let seqno = await wallet.getSeqno(provider);
    await openedWallet.sendTransfer({ seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano('0.3'), body: bonusBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) break; }
    await sleep(10000);

    let jet = await getJettonBal(client, pJetton);
    let ton = await getBal(client, wallet.address);
    let challBal = await getBal(client, challengeAddr);
    console.log(`After Bonus: Jetton=${jet} TON=${Number(ton)/1e9} Chall=${Number(challBal)/1e9}`);

    if (jet === null || jet < 1n) { console.log(`No jettons`); return; }

    // === TRADE: Sell 1 jetton via Transfer + Sell forward ===
    // Track TON before and after to see the actual payout
    console.log(`\n=== Sell 1 jetton ===`);
    const sellBody = beginCell()
        .storeUint(0x0f8a7ea5, 32).storeUint(0, 64)
        .storeCoins(1n).storeAddress(cJetton).storeAddress(null)
        .storeBit(0).storeCoins(toNano('0.05'))
        .storeUint(0x13370004, 32).storeUint(0, 64)
    .endCell();

    const walletTonBefore = await getBal(client, wallet.address);
    const challTonBefore = await getBal(client, challengeAddr);
    const cJetBalBefore = await getJettonBal(client, cJetton);
    console.log(`Before: Wallet TON=${Number(walletTonBefore)/1e9} Chall=${Number(challTonBefore)/1e9} cJetton=${cJetBalBefore}`);

    seqno = await wallet.getSeqno(provider);
    await openedWallet.sendTransfer({ seqno, secretKey: kp.secretKey,
        messages: [internal({ to: pJetton, value: toNano('0.15'), body: sellBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) break; }
    await sleep(20000);

    const walletTonAfter = await getBal(client, wallet.address);
    const challTonAfter = await getBal(client, challengeAddr);
    const pJetAfter = await getJettonBal(client, pJetton);
    const cJetAfter = await getJettonBal(client, cJetton);

    console.log(`After sell:`);
    console.log(`  Wallet: ${Number(walletTonBefore)/1e9} → ${Number(walletTonAfter)/1e9} (Δ=${Number(walletTonAfter-walletTonBefore)/1e9})`);
    console.log(`  Chall:  ${Number(challTonBefore)/1e9} → ${Number(challTonAfter)/1e9} (Δ=${Number(challTonAfter-challTonBefore)/1e9})`);
    console.log(`  pJetton: ${jet} → ${pJetAfter}`);
    console.log(`  cJetton: ${cJetBalBefore} → ${cJetAfter}`);

    // The TON difference: walletTonAfter - walletTonBefore
    // If Sell paid 2*1=2 TON, wallet TON would INCREASE significantly despite sending 0.15 TON
    const tonDiff = Number(walletTonAfter - walletTonBefore) / 1e9;
    if (tonDiff > 1.0) {
        console.log(`\n🔥 SELL PAID TOKEN_PRICE! Jetton sold for ~${tonDiff.toFixed(2)} TON!`);
    } else if (tonDiff > 0) {
        console.log(`\n✅ Sell paid ${tonDiff.toFixed(6)} TON (partial payout)`);
    } else {
        console.log(`\n❌ Sell paid nothing (net loss ${tonDiff.toFixed(6)} TON)`);
    }

    // Try isSolved
    for (let i = 0; i < 5; i++) {
        try { const r = await client.runMethod(challengeAddr, 'isSolved'); const ok = r.stack.readBoolean(); if (ok) { console.log(`\n🎉 SOLVED!`); process.exit(0); } } catch {}
        await sleep(3000);
    }
}
main().catch(console.error);
