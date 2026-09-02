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
    const cwc = beginCell().storeAddress(challengeAddr).endCell();
    const cwr = await client.runMethod(minter, 'get_wallet_address', [{ type: 'slice', cell: cwc } as TupleItem]);
    const cJetton = cwr.stack.readAddress();

    console.log(`Wallet: ${wallet.address}`);
    console.log(`Challenge: ${challengeAddr}`);
    console.log(`Minter: ${minter}`);
    console.log(`Player Jetton: ${pJetton}`);
    console.log(`Init: TON=${Number(await getBal(client, wallet.address))/1e9} Jetton=${await getJettonBal(client, pJetton)} Supply=${await getSupply(client, minter)}\n`);

    // Read challenge balance before
    let challBal = await getBal(client, challengeAddr);
    let minterBal = await getBal(client, minter);
    console.log(`Chall balance: ${Number(challBal)/1e9}`);
    console.log(`Minter balance: ${Number(minterBal)/1e9}\n`);

    // Bonus #1
    let seqno = await wallet.getSeqno(provider);
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();

    console.log(`Bonus #1: seqno=${seqno}, sending 0.3 TON...`);
    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano('0.3'), body: bonusBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) { console.log(`  → seqno ${ns}`); seqno = ns; break; } }
    await sleep(10000);

    challBal = await getBal(client, challengeAddr);
    minterBal = await getBal(client, minter);
    let j1 = await getJettonBal(client, pJetton);
    let s1 = await getSupply(client, minter);
    console.log(`  Chall=${Number(challBal)/1e9} Minter=${Number(minterBal)/1e9} Jetton=${j1} Supply=${s1}`);

    // Bonus #2
    console.log(`\nBonus #2: seqno=${seqno}, sending 0.3 TON...`);
    await openedWallet.sendTransfer({
        seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano('0.3'), body: bonusBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY,
    });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) { console.log(`  → seqno ${ns}`); seqno = ns; break; } }
    await sleep(15000);

    challBal = await getBal(client, challengeAddr);
    minterBal = await getBal(client, minter);
    let j2 = await getJettonBal(client, pJetton);
    let s2 = await getSupply(client, minter);
    console.log(`  Chall=${Number(challBal)/1e9} Minter=${Number(minterBal)/1e9} Jetton=${j2} Supply=${s2}`);

    // Bonus #3 - try with HIGH value (0.5)
    console.log(`\nBonus #3: seqno=${seqno}, sending 0.5 TON...`);
    let bal = await getBal(client, wallet.address);
    console.log(`  Wallet TON=${Number(bal)/1e9}`);
    if (bal > toNano('0.5')) {
        await openedWallet.sendTransfer({
            seqno, secretKey: kp.secretKey,
            messages: [internal({ to: challengeAddr, value: toNano('0.5'), body: bonusBody, bounce: false })],
            sendMode: SendMode.PAY_GAS_SEPARATELY,
        });
        for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) { console.log(`  → seqno ${ns}`); break; } }
        await sleep(10000);
        let s3 = await getSupply(client, minter);
        let j3 = await getJettonBal(client, pJetton);
        console.log(`  Supply=${s3} Jetton=${j3}`);
    }

    // Final state
    console.log(`\nFinal:`);
    console.log(`Supply=${await getSupply(client, minter)}`);
    console.log(`Jetton=${await getJettonBal(client, pJetton)}`);
    console.log(`Chall bal=${Number(await getBal(client, challengeAddr))/1e9}`);
    console.log(`Minter bal=${Number(await getBal(client, minter))/1e9}`);
}
main().catch(console.error);
