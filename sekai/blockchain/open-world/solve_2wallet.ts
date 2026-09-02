import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed } from '@ton/crypto';
import { randomBytes } from 'crypto';
import { Address, toNano, beginCell, SendMode, TupleItem, internal } from '@ton/core';
import * as fs from 'fs';

const SESSION_FILE = 'session.json';
interface SessionData { uuid: string; challenge: string; api: string; wallet_id: number; seed: string; }
function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

async function getBal(client: TonClient, addr: Address): Promise<bigint> { return client.getBalance(addr); }
async function getJettonBal(client: TonClient, addr: Address): Promise<bigint | null> {
    try { const r = await client.runMethod(addr, 'get_wallet_data'); return r.stack.readBigNumber(); } catch { return null; }
}
async function getSupply(client: TonClient, minter: Address): Promise<bigint | null> {
    try { const r = await client.runMethod(minter, 'get_jetton_data'); return r.stack.readBigNumber(); } catch { return null; }
}
async function waitSeqno(w: any, p: any, cur: number, label: string): Promise<number> {
    for (let t = 0; t < 30; t++) { await sleep(2000); const ns = await w.getSeqno(p); if (ns > cur) { console.log(`  ${label}: seqno ${cur}→${ns}`); return ns; } }
    console.log(`  ${label}: seqno STUCK at ${cur}`); return cur;
}
async function sendBonus(wallet: any, opened: any, provider: any, kp: any, challengeAddr: Address, value: string, label: string) {
    const body = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
    let seqno = await wallet.getSeqno(provider);
    await opened.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano(value), body, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    return waitSeqno(wallet, provider, seqno, label);
}

async function main() {
    const s: SessionData = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
    const client = new TonClient({ endpoint: s.api.replace(/\/+$/, '') + '/jsonRPC', timeout: 30000 });
    const challengeAddr = Address.parse(s.challenge);
    const kp = keyPairFromSeed(Buffer.from(s.seed, 'hex'));
    const wA = WalletContractV3R2.create({ workchain: -1, publicKey: kp.publicKey, walletId: s.wallet_id });
    const opA = client.open(wA);
    const prA = client.provider(wA.address, wA.init);

    // Get minter + jetton addresses
    const mr = await client.runMethod(challengeAddr, 'minter');
    const minter = mr.stack.readAddress();
    const pwc = (addr: Address) => beginCell().storeAddress(addr).endCell();
    const getJettonAddr = async (addr: Address) => {
        const r = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: pwc(addr) } as TupleItem]);
        return r.stack.readAddress();
    };
    const pJettonA = await getJettonAddr(wA.address);
    const cJetton = await getJettonAddr(challengeAddr);

    console.log(`Wallet A: ${wA.address}`);
    console.log(`Minter: ${minter}`);
    console.log(`A Jetton: ${pJettonA}`);
    console.log(`Init: TON=${Number(await getBal(client, wA.address))/1e9} Jetton=${await getJettonBal(client, pJettonA)}\n`);

    // === Step 1: Wallet A claims bonus ===
    await sendBonus(wA, opA, prA, kp.secretKey, challengeAddr, '0.2', 'A-bonus');
    await sleep(10000);
    let s1 = await getSupply(client, minter);
    let jA = await getJettonBal(client, pJettonA);
    console.log(`After A-bonus: Supply=${s1}, A Jetton=${jA}, A TON=${Number(await getBal(client, wA.address))/1e9}\n`);

    if (jA !== null && jA >= 100n) {
        console.log(`Already have 100 jettons!`);
    } else {
        // === Step 2: Create Wallet B and try PlayerBonus from B ===
        console.log(`=== Creating Wallet B ===`);
        const seedB = randomBytes(32);
        const kpB = keyPairFromSeed(seedB);
        const wB = WalletContractV3R2.create({ workchain: -1, publicKey: kpB.publicKey, walletId: Math.abs(~~(Math.random()*0x7fffffff)) });
        const opB = client.open(wB);
        const prB = client.provider(wB.address, wB.init);
        console.log(`Wallet B: ${wB.address}`);

        // Check if B is deployed
        const bDeployed = await client.isContractDeployed(wB.address);
        console.log(`B deployed: ${bDeployed}`);

        if (!bDeployed) {
            // Fund B from A
            const seqnoA = await wA.getSeqno(prA);
            console.log(`Funding B from A (seqno=${seqnoA}, A TON=${Number(await getBal(client, wA.address))/1e9})...`);
            await opA.sendTransfer({
                seqno: seqnoA, secretKey: kp.secretKey,
                messages: [internal({ to: wB.address, value: toNano('0.4'), bounce: false, init: wB.init })],
                sendMode: SendMode.PAY_GAS_SEPARATELY,
            });
            await waitSeqno(wA, prA, seqnoA, 'A-fund');
            await sleep(5000);
            const bDeployed2 = await client.isContractDeployed(wB.address);
            console.log(`B deployed after fund: ${bDeployed2}, B TON=${Number(await getBal(client, wB.address))/1e9}, A TON=${Number(await getBal(client, wA.address))/1e9}`);
        }

        // Wallet B calls PlayerBonus
        console.log(`\nWallet B claims PlayerBonus...`);
        const bBonusSeqno = await wB.getSeqno(prB);
        console.log(`B seqno=${bBonusSeqno}, B TON=${Number(await getBal(client, wB.address))/1e9}`);
        const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
        await opB.sendTransfer({
            seqno: bBonusSeqno, secretKey: kpB.secretKey,
            messages: [internal({ to: challengeAddr, value: toNano('0.2'), body: bonusBody, bounce: false })],
            sendMode: SendMode.PAY_GAS_SEPARATELY,
        });
        await waitSeqno(wB, prB, bBonusSeqno, 'B-bonus');
        await sleep(15000);

        // Check state
        const s2 = await getSupply(client, minter);
        const pJettonB = await getJettonAddr(wB.address);
        const jB = await getJettonBal(client, pJettonB);
        const jA2 = await getJettonBal(client, pJettonA);
        const bBal = await getBal(client, wB.address);
        console.log(`\nAfter B-bonus: Supply=${s2}`);
        console.log(`A Jetton=${jA2}, A TON=${Number(await getBal(client, wA.address))/1e9}`);
        console.log(`B Jetton=${jB}, B TON=${Number(bBal)/1e9}`);

        if (jB !== null && jB > 0n) {
            console.log(`\n🎉 Wallet B got ${jB} jettons! Transferring to A...`);
            const xferBody = beginCell()
                .storeUint(0x0f8a7ea5, 32).storeUint(0, 64)
                .storeCoins(jB).storeAddress(pJettonA).storeAddress(null)
                .storeBit(0).storeCoins(toNano('0.01'))
            .endCell();

            const bSeqno = await wB.getSeqno(prB);
            await opB.sendTransfer({
                seqno: bSeqno, secretKey: kpB.secretKey,
                messages: [internal({ to: pJettonB, value: toNano('0.15'), body: xferBody, bounce: false })],
                sendMode: SendMode.PAY_GAS_SEPARATELY,
            });
            await waitSeqno(wB, prB, bSeqno, 'B-xfer');
            await sleep(10000);

            const jA3 = await getJettonBal(client, pJettonA);
            console.log(`A Jetton after B's transfer: ${jA3}`);
            jA = jA3;
        }
    }

    // === Step 3: If A has 100 jettons, solve ===
    jA = await getJettonBal(client, pJettonA);
    console.log(`\n=== Final: A Jetton=${jA} ===`);

    if (jA === null || jA < 100n) {
        console.log(`Not enough.`);
        process.exit(1);
    }

    const xferBody = beginCell()
        .storeUint(0x0f8a7ea5, 32).storeUint(0, 64)
        .storeCoins(jA).storeAddress(cJetton).storeAddress(null)
        .storeBit(0).storeCoins(toNano('0.05'))
        .storeUint(0x13370005, 32).storeUint(0, 64)
    .endCell();

    const seqno = await wA.getSeqno(prA);
    console.log(`\nSolve: seqno=${seqno}, TON=${Number(await getBal(client, wA.address))/1e9}`);
    await opA.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: pJettonA, value: toNano('0.2'), body: xferBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    await waitSeqno(wA, prA, seqno, 'A-solve');
    await sleep(20000);

    for (let i = 0; i < 16; i++) {
        try { const r = await client.runMethod(challengeAddr, 'isSolved'); if (r.stack.readBoolean()) { console.log(`🎉 SOLVED! 🎉`); process.exit(0); } } catch {}
        await sleep(5000);
    }
    console.log(`Not solved.`);
}
main().catch(console.error);
