import { randomBytes, randomUUID } from 'crypto';
import { mkdir, readFile, readdir, rm, writeFile } from 'fs/promises';
import path from 'path';
import { keyPairFromSecretKey, keyPairFromSeed } from '@ton/crypto';
import { Address, OpenedContract, SendMode, toNano } from '@ton/core';
import { TonClient, WalletContractV3R2 } from '@ton/ton';
import { deployChallengeInstance, isChallengeInstanceSolved } from './deploy-challenge';
import { WalletContext } from './types';

type WalletSecretInfo = {
    version: 'v3r2';
    workchain: number;
    walletId: number;
    address: Address;
    walletSeedHex: string;
    publicKeyHex: string;
};

type ChallengeInfo = {
    address: Address;
    nonce: string;
};

export type LocalchainSessionRecord = {
    uuid: string;
    createdAt: string;
    expiresAt: string;
    player: WalletSecretInfo;
    challenge: ChallengeInfo;
};

export type LocalchainSessionView = LocalchainSessionRecord & {
    apiV2Endpoint: string;
    timeToLive: number;
};

export type KillSessionResult = {
    uuid: string;
    closedAt: string;
    reason: 'manual' | 'expired' | 'already closed';
    reclaimed: {
        player: string;
    };
};

type LocalchainConfig = {
    sessionDir: string;
    publicBaseUrl: string;
    sharedDataDir: string;
    mainWalletKeyPath: string;
    internalApiV2BaseUrl: string;
    internalConfigBaseUrl: string;
    workchain: number;
    mainWalletId: number;
    playerInitialBalance: bigint;
    challengeDeployValue: bigint;
    pollIntervalMs: number;
    waitTimeoutMs: number;
    instanceTtlMs: number;
    sessionSweepIntervalMs: number;
};

export class SessionLifecycleError extends Error {
    constructor(message: string, readonly statusCode: number) {
        super(message);
        this.name = 'SessionLifecycleError';
    }
}

const DEFAULT_PLAYER_INITIAL_BALANCE = '1';
const DEFAULT_INSTANCE_TTL_MS = '600000';
const DEFAULT_SWEEP_INTERVAL_MS = '30000';
const DEFAULT_SHARED_DATA_DIR = '/ton-shared';
const DEFAULT_PUBLIC_BASE_URL = 'http://127.0.0.1:3000';
const PUBLIC_HOST_PREFIX = 'open-world-api';

const closingSessions = new Set<string>();
let sweeperStarted = false;
let sharedTonClient: TonClient | undefined;
let mainWalletContextPromise: Promise<WalletContext> | undefined;

function publicBaseUrlFromRctfExpose() {
    const rawExpose = process.env.RCTF_EXPOSED_HOSTNAMES;
    if (!rawExpose) {
        return undefined;
    }

    try {
        const exposed = JSON.parse(rawExpose);
        const endpoint = Array.isArray(exposed)
            ? exposed.find((entry) => entry?.hostPrefix === PUBLIC_HOST_PREFIX && typeof entry.host === 'string')
            : undefined;
        return endpoint ? `https://${endpoint.host}` : undefined;
    } catch {
        return undefined;
    }
}

const config: LocalchainConfig = {
    sessionDir: process.env.SESSION_DIR ?? path.join(process.cwd(), '.localchain-sessions'),
    publicBaseUrl: (publicBaseUrlFromRctfExpose() ?? process.env.PUBLIC_BASE_URL ?? DEFAULT_PUBLIC_BASE_URL).replace(/\/$/, ''),
    sharedDataDir: process.env.SHARED_DATA_DIR ?? DEFAULT_SHARED_DATA_DIR,
    mainWalletKeyPath: process.env.MAIN_WALLET_PK_PATH ?? path.join(process.env.SHARED_DATA_DIR ?? DEFAULT_SHARED_DATA_DIR, 'main-wallet.pk'),
    internalApiV2BaseUrl: (process.env.INTERNAL_TON_API_V2_BASE_URL ?? 'http://tonhttpapi:8081/api/v2').replace(/\/$/, ''),
    internalConfigBaseUrl: (process.env.INTERNAL_CONFIG_BASE_URL ?? 'http://file-server:8000').replace(/\/$/, ''),
    workchain: Number(process.env.MAIN_WALLET_WORKCHAIN ?? '-1'),
    mainWalletId: Number(process.env.MAIN_WALLET_WALLET_ID ?? '42'),
    playerInitialBalance: toNano(process.env.PLAYER_INITIAL_BALANCE ?? DEFAULT_PLAYER_INITIAL_BALANCE),
    challengeDeployValue: toNano(process.env.CHALLENGE_DEPLOY_VALUE ?? '2'),
    pollIntervalMs: Number(process.env.CHAIN_POLL_INTERVAL_MS ?? '1500'),
    waitTimeoutMs: Number(process.env.CHAIN_WAIT_TIMEOUT_MS ?? '60000'),
    instanceTtlMs: Number(process.env.INSTANCE_TTL_MS ?? DEFAULT_INSTANCE_TTL_MS),
    sessionSweepIntervalMs: Number(process.env.SESSION_SWEEP_INTERVAL_MS ?? DEFAULT_SWEEP_INTERVAL_MS),
};

function createTonClient(endpoint: string) {
    return new TonClient({
        endpoint,
        timeout: config.waitTimeoutMs,
    });
}

function getSharedTonClient() {
    if (!sharedTonClient) {
        sharedTonClient = createTonClient(`${config.internalApiV2BaseUrl}/jsonRPC`);
    }

    return sharedTonClient;
}

function parseSeed(data: Buffer) {
    if (data.length === 32) {
        return data;
    }

    const normalized = data.toString('utf8').trim();
    if (/^[0-9a-fA-F]+$/.test(normalized)) {
        return Buffer.from(normalized, 'hex');
    }

    throw new Error('Unsupported key format');
}

function buildPublicUrl(pathname: string) {
    return `${config.publicBaseUrl}${pathname}`;
}

async function waitFor(condition: () => Promise<boolean>, timeoutMs: number, label: string) {
    const startedAt = Date.now();

    while (Date.now() - startedAt < timeoutMs) {
        if (await condition()) {
            return;
        }

        await new Promise((resolve) => setTimeout(resolve, config.pollIntervalMs));
    }

    throw new Error(`Timed out while waiting for ${label}`);
}

async function waitForWalletSeqnoIncrease(wallet: OpenedContract<WalletContractV3R2>, currentSeqno: number) {
    await waitFor(async () => (await wallet.getSeqno()) > currentSeqno, config.waitTimeoutMs, 'wallet seqno to increase');
}

async function waitForDeploy(client: TonClient, address: Address) {
    await waitFor(async () => client.isContractDeployed(address), config.waitTimeoutMs, `deployment of ${address.toRawString()}`);
}

function createWallet(client: TonClient, workchain: number) {
    const seed = randomBytes(32);
    const keyPair = keyPairFromSeed(seed);
    const walletId = Math.max(1, randomBytes(4).readUInt32BE(0) & 0x7fffffff);
    const wallet = client.open(WalletContractV3R2.create({
        workchain,
        publicKey: keyPair.publicKey,
        walletId,
    }));

    return {
        seed,
        keyPair,
        wallet,
        sender: wallet.sender(keyPair.secretKey),
    };
}

function createWalletInfo(seed: Buffer, keyPair: ReturnType<typeof keyPairFromSeed>, wallet: OpenedContract<WalletContractV3R2>): WalletSecretInfo {
    return {
        version: 'v3r2',
        workchain: wallet.workchain,
        walletId: wallet.walletId,
        address: wallet.address,
        walletSeedHex: seed.toString('hex'),
        publicKeyHex: keyPair.publicKey.toString('hex'),
    };
}

function buildWalletContextFromSecretInfo(client: TonClient, walletInfo: WalletSecretInfo): WalletContext {
    const seed = Buffer.from(walletInfo.walletSeedHex, 'hex');
    const keyPair = keyPairFromSeed(seed);
    const wallet = client.open(WalletContractV3R2.create({
        workchain: walletInfo.workchain,
        publicKey: keyPair.publicKey,
        walletId: walletInfo.walletId,
    }));

    return {
        wallet,
        sender: wallet.sender(keyPair.secretKey),
    };
}

function getSessionPath(uuid: string) {
    return path.join(config.sessionDir, `${uuid}.json`);
}

async function saveSession(session: LocalchainSessionRecord) {
    await mkdir(config.sessionDir, { recursive: true });
    await writeFile(getSessionPath(session.uuid), JSON.stringify(session, (_key, value) => {
        if (value instanceof Address) {
            return value.toString();
        }
        return value;
    }, 2), 'utf8');
}

async function loadSession(uuid: string) {
    const content = await readFile(getSessionPath(uuid), 'utf8');
    const session = JSON.parse(content) as LocalchainSessionRecord;

    session.player.address = parseStoredAddress(session.player.address);
    session.challenge.address = parseStoredAddress(session.challenge.address);
    return session;
}

function parseStoredAddress(value: unknown): Address {
    if (value instanceof Address) {
        return value;
    }
    
    if (typeof value === 'string') {
        return Address.parse(value);
    }

    throw new Error('invalid address');
}

function isExpired(session: LocalchainSessionRecord) {
    return new Date(session.expiresAt).getTime() <= Date.now();
}

function toSessionView(session: LocalchainSessionRecord): LocalchainSessionView {
    return {
        uuid: session.uuid,
        createdAt: session.createdAt,
        expiresAt: session.expiresAt,
        player: session.player,
        challenge: session.challenge,
        apiV2Endpoint: buildPublicUrl(`/instance/${session.uuid}/api/v2`),
        timeToLive: config.instanceTtlMs,
    };
}

async function getSharedMainWalletContext() {
    if (!mainWalletContextPromise) {
        mainWalletContextPromise = (async () => {
            await waitFor(async () => {
                try {
                    const key = await readFile(config.mainWalletKeyPath);
                    return key.length > 0;
                } catch {
                    return false;
                }
            }, config.waitTimeoutMs, 'shared main wallet key');

            const client = getSharedTonClient();
            const key = parseSeed(await readFile(config.mainWalletKeyPath));
            const keyPair = key.length === 32 ? keyPairFromSeed(key) : keyPairFromSecretKey(key);

            const wallet = client.open(WalletContractV3R2.create({
                workchain: config.workchain,
                publicKey: keyPair.publicKey,
                walletId: config.mainWalletId,
            }));

            return {
                wallet,
                sender: wallet.sender(keyPair.secretKey),
            };
        })().catch((error) => {
            mainWalletContextPromise = undefined;
            throw error;
        });
    }

    return mainWalletContextPromise;
}

async function fundWallet(client: TonClient, walletToFund: ReturnType<typeof createWallet>, mainWallet: WalletContext, amount: bigint) {
    const currentSeqno = await mainWallet.wallet.getSeqno();

    await mainWallet.sender.send({
        to: walletToFund.wallet.address,
        value: amount,
        bounce: false,
        init: walletToFund.wallet.init,
    });

    await waitForWalletSeqnoIncrease(mainWallet.wallet, currentSeqno);
    await waitForDeploy(client, walletToFund.wallet.address);
}

async function deployChallenge(client: TonClient, mainWallet: WalletContext, playerWallet: WalletContext) {
    const currentSeqno = await mainWallet.wallet.getSeqno();
    const challenge = await deployChallengeInstance(client, mainWallet, playerWallet, config.challengeDeployValue);

    await waitForWalletSeqnoIncrease(mainWallet.wallet, currentSeqno);
    await waitForDeploy(client, challenge.address);

    return challenge;
}

async function loadActiveSession(uuid: string) {
    let session: LocalchainSessionRecord;
    try {
        session = await loadSession(uuid);
    } catch {
        throw new SessionLifecycleError('Unknown session', 404);
    }

    if (isExpired(session)) {
        await closeSession(session, 'expired');
        throw new SessionLifecycleError('Session expired', 410);
    }

    return session;
}

async function reclaimWalletBalance(client: TonClient, walletInfo: WalletSecretInfo, mainWalletAddress: Address) {
    const walletContext = buildWalletContextFromSecretInfo(client, walletInfo);
    const balance = await client.getBalance(walletInfo.address).catch(() => 0n);

    if (balance <= 0n) {
        return 0n;
    }

    const currentSeqno = await walletContext.wallet.getSeqno();
    await walletContext.sender.send({
        to: mainWalletAddress,
        value: 0n,
        bounce: false,
        sendMode: SendMode.CARRY_ALL_REMAINING_BALANCE + SendMode.DESTROY_ACCOUNT_IF_ZERO,
    });
    await waitForWalletSeqnoIncrease(walletContext.wallet, currentSeqno).catch(() => undefined);

    return balance;
}

export async function isChallengeSolved(uuid: string) {
    const session = await loadActiveSession(uuid);
    const client = getSharedTonClient();
    return isChallengeInstanceSolved(client, session.challenge.address);
}

async function closeSession(session: LocalchainSessionRecord, reason: 'manual' | 'expired'): Promise<KillSessionResult> {
    if (closingSessions.has(session.uuid)) {
        return {
            uuid: session.uuid,
            closedAt: new Date().toISOString(),
            reason: 'already closed',
            reclaimed: {
                player: '0',
            },
        };
    }

    closingSessions.add(session.uuid);

    try {
        const client = getSharedTonClient();
        const mainWallet = await getSharedMainWalletContext();
        const playerReclaim = await reclaimWalletBalance(client, session.player, mainWallet.wallet.address).catch(() => 0n);

        await rm(getSessionPath(session.uuid), { force: true });

        return {
            uuid: session.uuid,
            closedAt: new Date().toISOString(),
            reason,
            reclaimed: {
                player: playerReclaim.toString(),
            },
        };
    } finally {
        closingSessions.delete(session.uuid);
    }
}

export async function createLocalchainSession() {
    const uuid = randomUUID();
    const client = getSharedTonClient();
    const mainWallet = await getSharedMainWalletContext();
    const playerWallet = createWallet(client, config.workchain);

    await fundWallet(client, playerWallet, mainWallet, config.playerInitialBalance);
    const challenge = await deployChallenge(client, mainWallet, playerWallet);

    const createdAt = new Date();
    const expiresAt = new Date(createdAt.getTime() + config.instanceTtlMs);

    const session: LocalchainSessionRecord = {
        uuid,
        createdAt: createdAt.toISOString(),
        expiresAt: expiresAt.toISOString(),
        player: createWalletInfo(playerWallet.seed, playerWallet.keyPair, playerWallet.wallet),
        challenge: {
            address: challenge.address,
            nonce: challenge.nonce.toString(),
        },
    };

    await saveSession(session);
    return toSessionView(session);
}

export async function killLocalchainSession(uuid: string, reason: 'manual' | 'expired' = 'manual') {
    const session = await loadSession(uuid).catch(() => {
        throw new SessionLifecycleError('Unknown session', 404);
    });

    return closeSession(session, reason);
}

export async function reapExpiredSessions() {
    const entries = await readdir(config.sessionDir).catch(() => [] as string[]);
    await Promise.all(entries.filter((entry) => entry.endsWith('.json')).map(async (entry) => {
        const uuid = entry.replace(/\.json$/, '');
        const session = await loadSession(uuid).catch(() => undefined);
        if (session && isExpired(session)) {
            await closeSession(session, 'expired').catch(() => undefined);
        }
    }));
}

export function startLocalchainSessionReaper() {
    if (sweeperStarted) {
        return;
    }

    sweeperStarted = true;
    void reapExpiredSessions();

    const timer = setInterval(() => {
        void reapExpiredSessions();
    }, config.sessionSweepIntervalMs);

    timer.unref();
}

export async function proxyLocalchainRequest(uuid: string, target: 'api-v2' | 'config', suffix: string, init?: RequestInit) {
    await loadActiveSession(uuid);

    let baseUrl: string;
    switch (target) {
        case 'api-v2':
            baseUrl = config.internalApiV2BaseUrl;
            break;
        case 'config':
            baseUrl = config.internalConfigBaseUrl;
            break;
    }

    const normalizedSuffix = suffix.startsWith('/') ? suffix : `/${suffix}`;
    return fetch(`${baseUrl}${normalizedSuffix}`, init);
}
