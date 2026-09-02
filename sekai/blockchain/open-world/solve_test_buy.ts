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

    console.log(`Init: TON=${Number(await getBal(client, wallet.address))/1e9}\n`);

    // Bonus
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
    await sendXfer(openedWallet, wallet, provider, kp, internal({ to: challengeAddr, value: toNano('0.15'), body: bonusBody, bounce: false }));
    await sleep(10000);
    let j = await getJettonBal(client, pJetton);
    console.log(`After bonus: Jetton=${j} TON=${Number(await getBal(client, wallet.address))/1e9}`);

    // Buy(50) with cheap amount to test if TOKEN_PRICE is 0 on deployed code
    console.log(`\nTesting Buy(50) with 0.15 TON (fails if TOKEN_PRICE=2, passes if TOKEN_PRICE=0)...`);
    const buyBody = beginCell().storeUint(0x13370003, 32).storeUint(0, 64).storeCoins(50n).endCell();
    try {
        await sendXfer(openedWallet, wallet, provider, kp, internal({ to: challengeAddr, value: toNano('0.15'), body: buyBody, bounce: false }));
        await sleep(10000);
        const j2 = await getJettonBal(client, pJetton);
        console.log(`Jetton: ${j2} (change: ${j2 !== null && j !== null ? Number(j2 - j) : '?'})`);
    } catch (e) {
        console.log(`Tx failed: ${e instanceof Error ? e.message.slice(0, 100) : e}`);
    }

    console.log(`\nFinal: Jetton=${await getJettonBal(client, pJetton)} TON=${Number(await getBal(client, wallet.address))/1e9}`);

    // Try Solve with whatever we have
    j = await getJettonBal(client, pJetton);
    if (j !== null && j >= 100n) {
        const xferBody = beginCell()
            .storeUint(0x0f8a7ea5, 32).storeUint(0, 64)
            .storeCoins(j).storeAddress(cJetton).storeAddress(null)
            .storeBit(0).storeCoins(toNano('0.05'))
            .storeUint(0x13370005, 32).storeUint(0, 64)
        .endCell();
        await sendXfer(openedWallet, wallet, provider, kp, internal({ to: pJetton, value: toNano('0.2'), body: xferBody, bounce: false }));
        await sleep(15000);

        for (let i = 0; i < 16; i++) {
            try { const r = await client.runMethod(challengeAddr, 'isSolved'); if (r.stack.readBoolean()) { console.log(`🎉 SOLVED!`); process.exit(0); } } catch {}
            await sleep(5000);
        }
    }
}
main().catch(console.error);
