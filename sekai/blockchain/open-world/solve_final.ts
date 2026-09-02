import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed } from '@ton/crypto';
import { Address, toNano, beginCell, SendMode, TupleItem, internal } from '@ton/core';
import * as fs from 'fs';

const SESSION_FILE = 'session.json';
interface SessionData { uuid: string; challenge: string; api: string; wallet_id: number; seed: string; }
function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

async function getBal(client: TonClient, addr: Address) { return client.getBalance(addr); }
async function getJettonBal(client: TonClient, addr: Address): Promise<bigint | null> {
    try { const r = await client.runMethod(addr, 'get_wallet_data'); return r.stack.readBigNumber(); } catch { return null; }
}

async function sendXfer(openedWallet: any, wallet: any, provider: any, kp: any, msg: any) {
    const seqno = await wallet.getSeqno(provider);
    console.log(`  seqno=${seqno}, sending msg...`);
    await openedWallet.sendTransfer({ seqno, secretKey: kp.secretKey, messages: [msg], sendMode: SendMode.PAY_GAS_SEPARATELY });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) { console.log(`  seqno→${ns}`); return; } }
    throw new Error(`seqno stuck`);
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

    const mr = await client.runMethod(challengeAddr, 'minter');
    const minter = mr.stack.readAddress();
    const pwc = beginCell().storeAddress(wallet.address).endCell();
    const pwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: pwc } as TupleItem]);
    const pJetton = pwr.stack.readAddress();
    const cwc = beginCell().storeAddress(challengeAddr).endCell();
    const cwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: cwc } as TupleItem]);
    const cJetton = cwr.stack.readAddress();
    console.log(`\npJetton: ${pJetton}\ncJetton: ${cJetton}\n`);

    let jetBal = await getJettonBal(client, pJetton);
    let tonBal = await getBal(client, wallet.address);
    console.log(`Current: Jetton=${jetBal} TON=${Number(tonBal)/1e9}`);

    // If no jettons, claim bonus
    if (jetBal === null || jetBal < 10n) {
        console.log(`Need jettons. Claiming bonus...`);
        const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
        await sendXfer(openedWallet, wallet, provider, kp, internal({ to: challengeAddr, value: toNano('0.35'), body: bonusBody, bounce: false }));
        await sleep(15000);
        jetBal = await getJettonBal(client, pJetton);
        tonBal = await getBal(client, wallet.address);
        console.log(`After Bonus: Jetton=${jetBal} TON=${Number(tonBal)/1e9}`);
    }

    if (jetBal === null || jetBal < 1n) {
        console.log(`No jettons. Abort.`);
        return;
    }

    // Now send ALL jettons to cJetton with Solve forward
    // Use minimal values to save TON
    console.log(`\n=== Sending ${jetBal} jettons + Solve ===`);
    const forwardTon = toNano('0.05'); // enough for TransferNotification at challenge
    const xferBody = beginCell()
        .storeUint(0x0f8a7ea5, 32).storeUint(0, 64)
        .storeCoins(jetBal).storeAddress(cJetton).storeAddress(null)
        .storeBit(0).storeCoins(forwardTon)
        .storeUint(0x13370005, 32).storeUint(0, 64) // Solve op
    .endCell();

    const msgVal = toNano('0.2'); // enough to cover deploy cJetton + forward
    tonBal = await getBal(client, wallet.address);
    console.log(`  TON balance before: ${Number(tonBal)/1e9}`);
    console.log(`  Sending ${Number(msgVal)/1e9} TON to pJetton`);

    try {
        await sendXfer(openedWallet, wallet, provider, kp, internal({ to: pJetton, value: msgVal, body: xferBody, bounce: false }));
        await sleep(20000);
    } catch (e: any) {
        console.log(`  Transfer failed: ${e.message.slice(0, 100)}`);
    }

    const afterJet = await getJettonBal(client, pJetton);
    console.log(`\nAfter: player jetton=${afterJet}`);
    console.log(`TON: ${Number(await getBal(client, wallet.address))/1e9}`);

    const cjBal = await getJettonBal(client, cJetton);
    console.log(`cJetton balance: ${cjBal}`);

    // Check isSolved
    console.log(`\n=== Checking isSolved ===`);
    for (let i = 0; i < 30; i++) {
        try {
            const r = await client.runMethod(challengeAddr, 'isSolved');
            if (r.stack.readBoolean()) {
                console.log(`\n🎉 SOLVED! 🎉\nUUID: ${s.uuid}`);
                process.exit(0);
            }
            console.log(`  Check ${i+1}: false`);
        } catch {}
        await sleep(5000);
    }
    console.log(`\nNot solved.`);
}
main().catch(console.error);
