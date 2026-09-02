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

async function claimBonus(openedWallet: any, wallet: any, provider: any, kp: any, challengeAddr: Address, value: string): Promise<{seqno: number, ok: boolean}> {
    let seqno = await wallet.getSeqno(provider);
    const body = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();

    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano(value), body, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });

    let ok = false;
    for (let w = 0; w < 30; w++) {
        await sleep(2000);
        const ns = await wallet.getSeqno(provider);
        if (ns > seqno) { seqno = ns; ok = true; break; }
    }
    return { seqno, ok };
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
    console.log(`Initial: TON=${Number(tonBal)/1e9} Jetton=${jetBal} Supply=${supply}\n`);

    // === Try multiple bonus claims with higher values ===
    const bonusValues = ['0.3', '0.3', '0.5'];

    for (let i = 0; i < bonusValues.length; i++) {
        tonBal = await client.getBalance(wallet.address);
        if (tonBal < toNano('0.2')) {
            console.log(`Balance too low for bonus #${i+1} (${Number(tonBal)/1e9} TON). Stopping.`);
            break;
        }

        const beforeSupply = await getMinterSupply(client, minter);
        const beforeJet = await getJettonBal(client, pJetton);

        console.log(`Bonus #${i+1} (value=${bonusValues[i]} TON):`);
        const {seqno, ok} = await claimBonus(openedWallet, wallet, provider, kp, challengeAddr, bonusValues[i]);
        console.log(`  Seqno: ${ok ? seqno : 'unchanged'}`);

        await sleep(8000); // extra settle

        tonBal = await client.getBalance(wallet.address);
        const afterSupply = await getMinterSupply(client, minter);
        const afterJet = await getJettonBal(client, pJetton);

        console.log(`  TON=${Number(tonBal)/1e9} Jetton=${afterJet}`);
        console.log(`  Supply: ${beforeSupply} → ${afterSupply}`);

        if (afterSupply && beforeSupply && afterSupply > beforeSupply) {
            console.log(`  ✅ Mint succeeded! +${Number(afterSupply - beforeSupply)} jettons`);
        } else if (ok) {
            console.log(`  ⚠️  Seqno advanced but no mint!`);
        }

        if (afterJet !== null && afterJet >= 100n) {
            console.log(`\n🎉 Have ${afterJet} jettons! Ready to solve.`);
            break;
        }
    }

    // === Transfer with Solve ===
    jetBal = await getJettonBal(client, pJetton);
    console.log(`\n=== Final jetton balance: ${jetBal} ===`);

    if (jetBal === null || jetBal < 100n) {
        console.log(`Not enough jettons (need 100, have ${jetBal})`);
        process.exit(1);
    }

    const xferBody = beginCell()
        .storeUint(0x0f8a7ea5, 32).storeUint(0, 64)
        .storeCoins(jetBal).storeAddress(cJetton).storeAddress(null)
        .storeBit(0).storeCoins(toNano('0.05'))
        .storeUint(0x13370005, 32).storeUint(0, 64)
    .endCell();

    let seqno = await wallet.getSeqno(provider);
    console.log(`Transfer: seqno=${seqno}, TON=${Number(await client.getBalance(wallet.address))/1e9}`);

    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: pJetton, value: toNano('0.25'), body: xferBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });

    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) { console.log(`  seqno→${ns}`); break; } }
    await sleep(15000); // wait for state to settle

    // Check isSolved
    console.log(`\n=== isSolved ===`);
    for (let i = 0; i < 16; i++) {
        try {
            const r = await client.runMethod(challengeAddr, 'isSolved');
            if (r.stack.readBoolean()) {
                console.log(`\n🎉 SOLVED! 🎉\nUUID: ${s.uuid}`);
                process.exit(0);
            }
            console.log(`  Check ${i+1}: false`);
        } catch (e: any) { console.log(`  Check ${i+1} error`); }
        await sleep(5000);
    }
    console.log(`\nNot solved.`);
}
main().catch(console.error);
