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
async function getSupply(client: TonClient, minter: Address): Promise<bigint | null> {
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

    // Get addrs
    const mr = await client.runMethod(challengeAddr, 'minter');
    const minter = mr.stack.readAddress();
    const pwc = beginCell().storeAddress(wallet.address).endCell();
    const pwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: pwc } as TupleItem]);
    const pJetton = pwr.stack.readAddress();
    const cwc = beginCell().storeAddress(challengeAddr).endCell();
    const cwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: cwc } as TupleItem]);
    const cJetton = cwr.stack.readAddress();

    console.log(`Wallet: ${wallet.address}\nMinter: ${minter}\nPlayer jetton: ${pJetton}\nChallenge jetton: ${cJetton}`);
    console.log(`Init: TON=${Number(await client.getBalance(wallet.address))/1e9} Jetton=${await getJettonBal(client, pJetton)} Supply=${await getSupply(client, minter)}\n`);

    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();

    async function sendBonus(n: number, value: string): Promise<boolean> {
        const bSeqno = await wallet.getSeqno(provider);
        console.log(`Bonus #${n} (${value} TON): seqno=${bSeqno}, TON=${Number(await client.getBalance(wallet.address))/1e9}`);
        await openedWallet.sendTransfer({
            seqno: bSeqno, secretKey: kp.secretKey,
            messages: [internal({ to: challengeAddr, value: toNano(value), body: bonusBody, bounce: false })],
            sendMode: SendMode.PAY_GAS_SEPARATELY,
        });
        for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > bSeqno) { break; } }
        await sleep(10000);

        const j = await getJettonBal(client, pJetton);
        const s = await getSupply(client, minter);
        console.log(`  TON=${Number(await client.getBalance(wallet.address))/1e9} Jetton=${j} Supply=${s}`);
        return j !== null && j >= 100n;
    }

    // Try up to 5 individual bonuses
    for (let i = 1; i <= 5; i++) {
        const bal = await client.getBalance(wallet.address);
        if (bal < toNano('0.2')) { console.log(`\nBalance too low (${Number(bal)/1e9} TON). Stop.`); break; }

        const done = await sendBonus(i, '0.2');
        if (done) {
            console.log(`\n✅ Have 100 jettons!`);
            break;
        }

        // Check if supply increased
        const s = await getSupply(client, minter);
        console.log(`  (total supply: ${s})`);
    }

    // Final state
    let jetBal = await getJettonBal(client, pJetton);
    console.log(`\nFinal: Jetton=${jetBal}`);

    if (jetBal !== null && jetBal >= 100n) {
        console.log(`\n=== Transfer ${jetBal} jettons + Solve ===`);
        const xferBody = beginCell()
            .storeUint(0x0f8a7ea5, 32).storeUint(0, 64)
            .storeCoins(jetBal).storeAddress(cJetton).storeAddress(null)
            .storeBit(0).storeCoins(toNano('0.05'))
            .storeUint(0x13370005, 32).storeUint(0, 64)
        .endCell();

        const s2 = await wallet.getSeqno(provider);
        console.log(`  seqno=${s2}, TON=${Number(await client.getBalance(wallet.address))/1e9}`);
        await openedWallet.sendTransfer({
            seqno: s2, secretKey: kp.secretKey,
            messages: [internal({ to: pJetton, value: toNano('0.2'), body: xferBody, bounce: false })],
            sendMode: SendMode.PAY_GAS_SEPARATELY,
        });
        for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > s2) { break; } }
        await sleep(15000);

        console.log(`\n=== isSolved ===`);
        for (let i = 0; i < 16; i++) {
            try { const r = await client.runMethod(challengeAddr, 'isSolved'); if (r.stack.readBoolean()) { console.log(`\n🎉 SOLVED! 🎉\nUUID: ${s.uuid}`); process.exit(0); } } catch {}
            await sleep(5000);
        }
    }
    console.log(`\nNot solved.`);
}
main().catch(console.error);
