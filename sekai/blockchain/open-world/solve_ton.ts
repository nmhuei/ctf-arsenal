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

async function getTotalSupply(client: TonClient, minter: Address): Promise<bigint | null> {
    try { const r = await client.runMethod(minter, 'get_jetton_data'); return r.stack.readBigNumber(); } catch { return null; }
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
    console.log(`Challenge jetton: ${cJetton}\n`);

    // Initial state
    let tonBal = await client.getBalance(wallet.address);
    let tSupply = await getTotalSupply(client, minter);
    let jetBal = await getJettonBal(client, pJetton);
    console.log(`Initial: TON=${Number(tonBal)/1e9} Jetton=${jetBal} Supply=${tSupply}`);

    // === Phase 1: Claim bonuses with seqno tracking ===
    console.log(`\n=== Bonus claims ===`);
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();

    for (let i = 1; i <= 2; i++) {
        let seqno = await wallet.getSeqno(provider);
        console.log(`\nBonus #${i}: seqno=${seqno}, TON=${Number(await client.getBalance(wallet.address))/1e9}`);

        await openedWallet.sendTransfer({
            seqno,
            secretKey: kp.secretKey,
            messages: [internal({
                to: challengeAddr,
                value: toNano('0.15'),
                body: bonusBody,
                bounce: false,
            })],
            sendMode: SendMode.PAY_GAS_SEPARATELY,
        });

        console.log(`  Waiting for seqno ${seqno} → next...`);
        let seqnoChanged = false;
        for (let w = 0; w < 30; w++) {
            await sleep(2000);
            const newSeqno = await wallet.getSeqno(provider);
            if (newSeqno > seqno) { console.log(`  Seqno now: ${newSeqno}`); seqnoChanged = true; break; }
            if (w === 29) console.log(`  WARNING: seqno still ${seqno} after 60s`);
        }

        await sleep(5000); // settle state

        tonBal = await client.getBalance(wallet.address);
        jetBal = await getJettonBal(client, pJetton);
        tSupply = await getTotalSupply(client, minter);
        console.log(`  TON=${Number(tonBal)/1e9} Jetton=${jetBal} Supply=${tSupply}`);

        if (!seqnoChanged) {
            console.log(`  ⚠️  Seqno didn't advance — bonus #${i} might have failed silently`);
        }
    }

    // === Phase 2: Transfer with Solve ===
    jetBal = await getJettonBal(client, pJetton);
    console.log(`\n=== Transfer ${jetBal ?? 0} jettons + Solve ===`);

    const amount = (jetBal ?? 0n);
    if (amount <= 0n) { console.log(`No jettons!`); process.exit(1); }

    const xferBody = beginCell()
        .storeUint(0x0f8a7ea5, 32) .storeUint(0, 64)
        .storeCoins(amount) .storeAddress(cJetton) .storeAddress(null)
        .storeBit(0) .storeCoins(toNano('0.05'))
        .storeUint(0x13370005, 32) .storeUint(0, 64)
    .endCell();

    let seqno = await wallet.getSeqno(provider);
    console.log(`Seqno: ${seqno}, Wallet TON: ${Number(await client.getBalance(wallet.address))/1e9}`);
    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: pJetton, value: toNano('0.2'), body: xferBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    console.log(`Waiting for transfer to confirm...`);
    for (let w = 0; w < 30; w++) {
        await sleep(2000);
        const ns = await wallet.getSeqno(provider);
        if (ns > seqno) { console.log(`Seqno now: ${ns}`); break; }
    }
    await sleep(10000);

    // === Phase 3: Check isSolved ===
    console.log(`\n=== Check isSolved ===`);
    for (let i = 0; i < 12; i++) {
        try {
            const r = await client.runMethod(challengeAddr, 'isSolved');
            const solved = r.stack.readBoolean();
            console.log(`Check ${i+1}: ${solved}`);
            if (solved) {
                console.log(`\n🎉 SOLVED! 🎉\nUUID: ${s.uuid}`);
                process.exit(0);
            }
        } catch (e: any) { console.log(`Check ${i+1} error: ${e.message.slice(0, 80)}`); }
        await sleep(5000);
    }
    console.log(`Not solved. Jetton after: ${await getJettonBal(client, pJetton)}`);
}
main().catch(console.error);
