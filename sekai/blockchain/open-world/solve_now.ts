import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed } from '@ton/crypto';
import { Address, toNano, beginCell, SendMode, TupleItem, internal } from '@ton/core';
import * as fs from 'fs';

const SESSION_FILE = 'session.json';
interface SessionData { uuid: string; challenge: string; api: string; wallet_id: number; seed: string; }
function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

async function sendXfer(openedWallet: any, wallet: any, provider: any, kp: any, msg: any) {
    const seqno = await wallet.getSeqno(provider);
    await openedWallet.sendTransfer({ seqno, secretKey: kp.secretKey, messages: [msg], sendMode: SendMode.PAY_GAS_SEPARATELY });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) return; }
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
    console.log(`Wallet: ${wallet.address}\n`);

    const mr = await client.runMethod(challengeAddr, 'minter');
    const minter = mr.stack.readAddress();
    const pwc = beginCell().storeAddress(wallet.address).endCell();
    const pwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: pwc } as TupleItem]);
    const pJetton = pwr.stack.readAddress();
    const cwc = beginCell().storeAddress(challengeAddr).endCell();
    const cwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: cwc } as TupleItem]);
    const cJetton = cwr.stack.readAddress();
    console.log(`pJetton: ${pJetton}`);
    console.log(`cJetton: ${cJetton}\n`);

    // Claim player bonus
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
    await sendXfer(openedWallet, wallet, provider, kp, internal({ to: challengeAddr, value: toNano('0.3'), body: bonusBody, bounce: false }));
    await sleep(15000);

    const jetBal = await getJettonBal(client, pJetton);
    const tonBal = await client.getBalance(wallet.address);
    console.log(`After Bonus: Jetton=${jetBal} TON=${Number(tonBal)/1e9}`);

    if (jetBal === null || jetBal < 100n) {
        console.log(`\nHave ${jetBal} jettons, need 100+`);
        console.log(`Trying: transfer ${jetBal} jettons with Solve anyway...`);

        // Transfer ALL jettons with Solve
        const xferBody = beginCell()
            .storeUint(0x0f8a7ea5, 32).storeUint(0, 64)
            .storeCoins(jetBal).storeAddress(cJetton).storeAddress(null)
            .storeBit(0).storeCoins(toNano('0.05'))
            .storeUint(0x13370005, 32).storeUint(0, 64)
        .endCell();

        const before = await client.getBalance(wallet.address);
        await sendXfer(openedWallet, wallet, provider, kp, internal({ to: pJetton, value: toNano('0.2'), body: xferBody, bounce: false }));
        await sleep(20000);

        const afterJet = await getJettonBal(client, pJetton);
        console.log(`\nAfter transfer: player jetton=${afterJet}`);
        console.log(`TON spent: ${Number(before - await client.getBalance(wallet.address))/1e9}`);

        // Check if jettons arrived at cJetton
        const cjBal = await getJettonBal(client, cJetton);
        console.log(`cJetton balance: ${cjBal}`);

        // Check isSolved
        for (let i = 0; i < 20; i++) {
            try {
                const r = await client.runMethod(challengeAddr, 'isSolved');
                if (r.stack.readBoolean()) { console.log(`\n🎉 SOLVED! 🎉\nUUID: ${s.uuid}`); process.exit(0); }
                console.log(`  isSolved check ${i+1}: false`);
            } catch {}
            await sleep(5000);
        }
    }
}

async function getJettonBal(client: TonClient, addr: Address): Promise<bigint | null> {
    try { const r = await client.runMethod(addr, 'get_wallet_data'); return r.stack.readBigNumber(); } catch { return null; }
}

main().catch(console.error);
