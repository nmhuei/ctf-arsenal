import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed } from '@ton/crypto';
import { Address, toNano, beginCell, SendMode, TupleItem, internal } from '@ton/core';
import * as fs from 'fs';

const SESSION_FILE = 'session.json';
interface SessionData { uuid: string; challenge: string; api: string; wallet_id: number; seed: string; }
function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

async function getJettonBal(client: TonClient, addr: Address): Promise<bigint | null> {
    try { const r = await client.runMethod(addr, 'get_wallet_data'); return r.stack.readBigNumber(); } catch { return null; }
}

async function main() {
    const s: SessionData = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
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
    console.log(`Point: ${pJetton}\nCJet: ${cJetton}\n`);

    // Claim 1 bonus
    let seqno = await wallet.getSeqno(provider);
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
    console.log(`Bonus #1: seqno=${seqno}...`);
    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano('0.2'), body: bonusBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) break; }
    await sleep(10000);
    let jetBal = await getJettonBal(client, pJetton);
    console.log(`Jetton: ${jetBal}`);

    // Try transfer 50 jettons with Solve (in case FLAG_PRICE=50 on deployed code)
    const amount = jetBal ?? 0n;
    console.log(`\nTransferring ${amount} jettons + Solve (checking if FLAG_PRICE=50)...`);
    const xferBody = beginCell()
        .storeUint(0x0f8a7ea5, 32).storeUint(0, 64)
        .storeCoins(amount).storeAddress(cJetton).storeAddress(null)
        .storeBit(0).storeCoins(toNano('0.05'))
        .storeUint(0x13370005, 32).storeUint(0, 64)
    .endCell();

    seqno = await wallet.getSeqno(provider);
    console.log(`seqno=${seqno}, TON=${Number(await client.getBalance(wallet.address))/1e9}`);
    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: pJetton, value: toNano('0.2'), body: xferBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) break; }
    await sleep(20000);

    console.log(`\n=== isSolved ===`);
    for (let i = 0; i < 16; i++) {
        try { const r = await client.runMethod(challengeAddr, 'isSolved'); const ok = r.stack.readBoolean(); console.log(`Check ${i+1}: ${ok}`); if (ok) { console.log(`\n🎉 SOLVED!`); process.exit(0); } } catch {}
        await sleep(5000);
    }
    console.log(`Not solved. Jetton: ${await getJettonBal(client, pJetton)}`);
}
main().catch(console.error);
