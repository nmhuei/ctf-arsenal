import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { keyPairFromSeed } from '@ton/crypto';
import { Address, toNano, beginCell, SendMode, TupleItem } from '@ton/core';
import * as tls from 'tls';
import * as crypto from 'crypto';

const HOST = 'open-world-ad339fb35916.instancer.sekai.team';
const PORT = 1337;

interface SessionInfo {
    uuid: string;
    challengeAddress: Address;
    apiEndpoint: string;
    walletId: number;
    walletSeedHex: string;
}

function solvePow(prefix: string, difficulty: number): string {
    const target = '0'.repeat(difficulty * 2);
    let nonce = 0;
    while (true) {
        const input = nonce.toString();
        const hash = crypto.createHash('sha256').update(prefix + input).digest('hex');
        if (hash.startsWith(target)) {
            console.log(`[PoW] Found: ${input} (hash: ${hash.slice(0, 16)}...)`);
            return input;
        }
        nonce++;
    }
}

async function getSession(): Promise<SessionInfo> {
    return new Promise((resolve, reject) => {
        const socket = tls.connect(PORT, HOST, { rejectUnauthorized: false }, () => {
            console.log('[+] TLS connected');
        });
        let buffer = '';
        let stage: 'welcome' | 'pow' | 'session' = 'welcome';
        const timeout = setTimeout(() => {
            socket.destroy();
            reject(new Error('Connection timeout'));
        }, 120000);

        socket.on('data', async (chunk) => {
            const text = chunk.toString();
            buffer += text;
            console.log(`[NC] chunk: ${JSON.stringify(text)}`);

            if (stage === 'welcome' && buffer.includes('action?')) {
                socket.write('1\n');
                buffer = '';
                stage = 'pow';
                return;
            }

            if (stage === 'pow') {
                const match = buffer.match(/sha256\("([^"]+)"\s*\+\s*YOUR_INPUT\) must start with (\d+) bytes zeros/);
                if (match) {
                    const prefix = match[1];
                    const difficulty = parseInt(match[2]);
                    console.log(`[PoW] Solving: sha256("${prefix}" + X) = 00...`);
                    const solution = solvePow(prefix, difficulty);
                    socket.write(solution + '\n');
                    buffer = '';
                    stage = 'session';
                    return;
                }
            }

            if (stage === 'session' && buffer.includes('uuid:')) {
                const lines = buffer.split('\n');
                const uuid = lines.find(l => l.includes('uuid:'))?.split('uuid:')[1]?.trim() || '';
                const challengeAddrRaw = lines.find(l => l.includes('challenge contract:'))?.split('challenge contract:')[1]?.trim() || '';
                const api = lines.find(l => l.includes('api v2:'))?.split('api v2:')[1]?.trim() || '';
                const walletIdRaw = lines.find(l => l.includes('your wallet id:'))?.split('your wallet id:')[1]?.trim() || '';
                const seed = lines.find(l => l.includes('seed:'))?.split('seed:')[1]?.trim() || '';

                clearTimeout(timeout);
                socket.destroy();
                resolve({
                    uuid,
                    challengeAddress: Address.parse(challengeAddrRaw),
                    apiEndpoint: api.replace(/\/+$/, ''),
                    walletId: parseInt(walletIdRaw),
                    walletSeedHex: seed,
                });
            }
        });

        socket.on('error', (err) => { clearTimeout(timeout); reject(err); });
    });
}

async function waitFor(ms: number = 5000): Promise<void> {
    await new Promise(r => setTimeout(r, ms));
}

async function main() {
    // === Step 1: Get session ===
    console.log('[*] Connecting to server...');
    const session = await getSession();
    console.log(`[+] UUID: ${session.uuid}`);
    console.log(`[+] Challenge: ${session.challengeAddress}`);
    console.log(`[+] API: ${session.apiEndpoint}`);
    console.log(`[+] Wallet ID: ${session.walletId}`);

    // === Step 2: Create client & wallet ===
    console.log('\n[*] Creating wallet...');
    const client = new TonClient({ endpoint: session.apiEndpoint, timeout: 30000 });

    const seed = Buffer.from(session.walletSeedHex, 'hex');
    const keyPair = keyPairFromSeed(seed);
    const wallet = WalletContractV3R2.create({ workchain: 0, publicKey: keyPair.publicKey, walletId: session.walletId });
    const openedWallet = client.open(wallet);
    const sender = openedWallet.sender(keyPair.secretKey);
    console.log(`[+] Wallet: ${wallet.address}`);

    await waitFor(2000);

    // === Step 3: Get minter address ===
    console.log('\n[*] Getting minter...');
    const minterResult = await client.runMethod(session.challengeAddress, 'minter');
    const minterAddress = minterResult.stack.readAddress();
    console.log(`[+] Minter: ${minterAddress}`);

    // === Step 4: Claim PlayerBonus twice ===
    console.log('\n[*] Claiming PlayerBonus x2...');
    const bonusBody = beginCell().storeUint(0x13370002, 32).storeUint(0, 64).endCell();

    for (let i = 1; i <= 2; i++) {
        console.log(`  -> Bonus #${i}`);
        await sender.send({
            to: session.challengeAddress,
            value: toNano('0.3'),
            body: bonusBody,
            sendMode: SendMode.PAY_GAS_SEPARATELY,
            bounce: false,
        });
        console.log(`  -> Sent, waiting...`);
        await waitFor(8000);
    }

    // === Step 5: Get jetton wallet addresses ===
    console.log('\n[*] Getting jetton wallets...');
    const addrSliceCell = beginCell().storeAddress(wallet.address).endCell();
    const pwResult = await client.runMethod(minterAddress, 'get_wallet_address', [
        { type: 'slice', cell: addrSliceCell } as TupleItem,
    ]);
    const playerJettonWallet = pwResult.stack.readAddress();
    console.log(`[+] Player jetton: ${playerJettonWallet}`);

    const addrSliceCell2 = beginCell().storeAddress(session.challengeAddress).endCell();
    const cwResult = await client.runMethod(minterAddress, 'get_wallet_address', [
        { type: 'slice', cell: addrSliceCell2 } as TupleItem,
    ]);
    const challengeJettonWallet = cwResult.stack.readAddress();
    console.log(`[+] Challenge jetton: ${challengeJettonWallet}`);

    // Check player jetton balance
    try {
        const wdResult = await client.runMethod(playerJettonWallet, 'get_wallet_data');
        const balance = wdResult.stack.readBigNumber();
        console.log(`[+] Player jetton balance: ${balance}`);
    } catch (e) {
        console.log(`  -> Balance check: ${e instanceof Error ? e.message : e}`);
    }

    // === Step 6: Transfer 100 jettons with Solve payload ===
    console.log('\n[*] Sending 100 jettons with Solve...');
    const askToTransferBody = beginCell()
        .storeUint(0x0f8a7ea5, 32)  // op - AskToTransfer
        .storeUint(0, 64)           // queryId
        .storeCoins(100n)           // jettonAmount = 100 (FLAG_PRICE)
        .storeAddress(challengeJettonWallet) // transferRecipient
        .storeAddress(null)          // sendExcessesTo (addr_none)
        .storeBit(0)                // customPayload = null
        .storeCoins(toNano('0.05')) // forwardTonAmount for gas
        .storeUint(0x13370005, 32)  // forwardPayload: Solve op
        .storeUint(0, 64)           // forwardPayload: queryId
    .endCell();

    await sender.send({
        to: playerJettonWallet,
        value: toNano('0.15'),
        body: askToTransferBody,
        sendMode: SendMode.PAY_GAS_SEPARATELY,
        bounce: false,
    });
    console.log('[+] Transfer sent!');
    await waitFor(10000);

    // === Step 7: Check isSolved ===
    console.log('\n[*] Checking isSolved...');
    for (let i = 0; i < 5; i++) {
        try {
            const result = await client.runMethod(session.challengeAddress, 'isSolved');
            const solved = result.stack.readBoolean();
            console.log(`  -> isSolved = ${solved}`);
            if (solved) {
                console.log('\n🎉 SOLVED! 🎉');
                console.log(`UUID: ${session.uuid}`);
                console.log('Connect back and use:\n  2 -> enter UUID -> flag');
                return;
            }
        } catch (e) {
            console.log(`  -> Check error: ${e instanceof Error ? e.message : e}`);
        }
        await waitFor(3000);
    }
    console.log('[!] Not solved after all checks');
}

main().catch(console.error);
