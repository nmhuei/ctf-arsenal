import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed, keyPairFromSecretKey } from '@ton/crypto';
import { Address, toNano, beginCell, SendMode, TupleItem, internal, Cell } from '@ton/core';
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

async function main() {
    const s: SessionData = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
    console.log(`UUID: ${s.uuid}`);
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

    console.log(`Challenge: ${challengeAddr}`);
    console.log(`Minter: ${minter}`);
    console.log(`pJetton: ${pJetton}`);
    console.log(`cJetton: ${cJetton}\n`);

    // === Get jetton wallet code from minter's get_jetton_data ===
    console.log('=== Reading minter data... ===');
    const jd = await client.runMethod(minter, 'get_jetton_data');
    // Stack: [totalSupply:int, mintable:bool, adminAddress:address, content:cell, jettonWalletCode:cell]
    const totalSupply = jd.stack.readBigNumber();
    const mintable = jd.stack.readBoolean();
    const adminAddress = jd.stack.readAddress();
    // Skip content cell, read the 5th item (jettonWalletCode)
    const rawResult = await client.runMethod(minter, 'get_jetton_data');
    const stack = rawResult.stack.items;
    console.log(`  totalSupply: ${totalSupply}`);
    console.log(`  mintable: ${mintable}`);
    console.log(`  adminAddress: ${adminAddress}`);
    console.log(`  Stack items: ${stack.length}`);

    // Try reading all items
    for (let i = 0; i < stack.length; i++) {
        const item = stack[i];
        console.log(`  Stack[${i}]: type=${item.type}`);
    }

    // === Also check wallet data from existing jetton wallet (after bonus) ===
    console.log(`\n=== Claiming bonus to create pJetton... ===`);
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
    let seqno = await wallet.getSeqno(provider);
    await openedWallet.sendTransfer({ seqno, secretKey: kp.secretKey,
        messages: [internal({ to: challengeAddr, value: toNano('0.3'), body: bonusBody, bounce: false })],
        sendMode: SendMode.PAY_GAS_SEPARATELY });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) break; }
    await sleep(12000);

    const jetData = await getJettonBal(client, pJetton);
    console.log(`  Jetton: ${jetData}`);

    // === Try reading pJetton's wallet data to get minter code ===
    console.log(`\n=== Reading pJetton wallet data... ===`);
    const wd = await client.runMethod(pJetton, 'get_wallet_data');
    // Stack: [balance:coins, ownerAddress:address, minterAddress:address, jettonWalletCode:cell]
    const bal = wd.stack.readBigNumber();
    const owner = wd.stack.readAddress();
    const minterFromWallet = wd.stack.readAddress();
    // codeCell = wd.stack.readCell()
    console.log(`  Balance: ${bal}`);
    console.log(`  Owner: ${owner}`);
    console.log(`  Minter: ${minterFromWallet}`);

    // Read the code cell
    try {
        const codeCell = wd.stack.readCell();
        const hash = codeCell.hash().toString('hex');
        console.log(`  Code cell hash: ${hash}`);
        console.log(`  Code cell bits: ${codeCell.bits.length}`);
        console.log(`  Ref count: ${codeCell.refs.length}`);

        // Save code cell for later use
        fs.writeFileSync('jetton_wallet_code.cell', codeCell.toBoc({ idx: true, crc32: true }));
        console.log(`  Saved jetton wallet code (${codeCell.toBoc({ idx: true, crc32: true }).length} bytes)`);
    } catch (e: any) {
        console.log(`  Code cell read error: ${e.message.slice(0, 100)}`);
    }

    console.log(`\n=== Done ===`);
}
main().catch(console.error);
