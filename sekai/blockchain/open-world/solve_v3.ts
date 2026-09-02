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

async function getJettonOwner(client: TonClient, addr: Address): Promise<Address | null> {
    try { const r = await client.runMethod(addr, 'get_wallet_data'); r.stack.readBigNumber(); return r.stack.readAddress(); } catch { return null; }
}

async function main() {
    const s: SessionData = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
    console.log(`UUID: ${s.uuid}\nChallenge: ${s.challenge}`);

    const client = new TonClient({ endpoint: s.api.replace(/\/+$/, '') + '/jsonRPC', timeout: 30000 });
    const challengeAddr = Address.parse(s.challenge);
    const kp = keyPairFromSeed(Buffer.from(s.seed, 'hex'));
    const wallet = WalletContractV3R2.create({ workchain: -1, publicKey: kp.publicKey, walletId: s.wallet_id });
    const openedWallet = client.open(wallet);
    const provider = client.provider(wallet.address, wallet.init);
    console.log(`Wallet: ${wallet.address}`);

    // Get minter + jetton addresses
    const mr = await client.runMethod(challengeAddr, 'minter');
    const minter = mr.stack.readAddress();
    const pwc = beginCell().storeAddress(wallet.address).endCell();
    const pwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: pwc } as TupleItem]);
    const pJetton = pwr.stack.readAddress();
    const cwc = beginCell().storeAddress(challengeAddr).endCell();
    const cwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: cwc } as TupleItem]);
    const cJetton = cwr.stack.readAddress();

    console.log(`Minter: ${minter}\nPlayer jetton: ${pJetton}\nChallenge jetton: ${cJetton}\n`);

    // Initial state
    let tonBal = await client.getBalance(wallet.address);
    let jetBal = await getJettonBal(client, pJetton);
    let supply = await getMinterSupply(client, minter);
    let jetOwner = await getJettonOwner(client, pJetton);
    console.log(`Initial: TON=${Number(tonBal)/1e9} Jetton=${jetBal} Supply=${supply} Owner=${jetOwner?.toString().slice(0, 30)}...\n`);

    // === Claim bonuses ===
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();

    async function tryBonus(label: string, value: string): Promise<boolean> {
        const bSeqno = await wallet.getSeqno(provider);
        console.log(`${label}: seqno=${bSeqno}, TON=${Number(await client.getBalance(wallet.address))/1e9}`);

        await openedWallet.sendTransfer({
            seqno: bSeqno, secretKey: kp.secretKey,
            messages: [internal({ to: challengeAddr, value: toNano(value), body: bonusBody, bounce: false })],
            sendMode: SendMode.PAY_GAS_SEPARATELY,
        });

        let advanced = false;
        for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > bSeqno) { advanced = true; break; } }
        if (advanced) console.log(`  seqno advanced ✓`);
        else { console.log(`  seqno STALLED ✗`); return false; }

        await sleep(10000); // settle

        const t = await client.getBalance(wallet.address);
        const j = await getJettonBal(client, pJetton);
        const s = await getMinterSupply(client, minter);
        const o = await getJettonOwner(client, pJetton);
        console.log(`  TON=${Number(t)/1e9} Jetton=${j} Supply=${s} Owner=${o?.toString().slice(0,30)}...`);
        return true;
    }

    // Bonus #1
    const r1 = await tryBonus("Bonus #1", "0.25");

    // Bonus #2
    const r2 = await tryBonus("Bonus #2", "0.25");

    // Check if we have 100
    supply = await getMinterSupply(client, minter);
    jetBal = await getJettonBal(client, pJetton);
    console.log(`\nAfter 2 bonuses: Supply=${supply}, Player Jetton=${jetBal}`);

    // If supply is 100 but player balance is 50, player jetton wallet is wrong
    if (supply === 100n && (jetBal === null || jetBal < 100n)) {
        console.log(`⚠️  Supply=100 but player jetton=${jetBal} — wrong jetton wallet address!`);

        // Try computing jetton wallet addresses differently
        console.log(`\n  Debug: computing alternative addresses...`);
        const pwc2 = beginCell().storeAddress(wallet.address).endCell();
        const pwr2 = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: pwc2 } as TupleItem]);
        const pJetton2 = pwr2.stack.readAddress();
        console.log(`  Same address? ${pJetton2.toString() === pJetton.toString()}`);

        // Check all jetton wallets for this minter
        const supply2 = await getMinterSupply(client, minter);
        console.log(`  Supply re-check: ${supply2}`);
        return;
    }

    if (jetBal === null || jetBal < 100n) {
        console.log(`Only ${jetBal} jettons.`);
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

    let seqno = await wallet.getSeqno(provider);
    console.log(`  seqno=${seqno}, TON=${Number(await client.getBalance(wallet.address))/1e9}`);
    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: pJetton, value: toNano('0.25'), body: xferBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) { console.log(`  seqno→${ns}`); break; } }
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
    console.log(`\nNot solved.`);
}
main().catch(console.error);
