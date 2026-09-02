import net from 'node:net';
import { createHash, randomBytes } from 'node:crypto';
import {
    createLocalchainSession,
    isChallengeSolved,
    killLocalchainSession,
    LocalchainSessionView,
    SessionLifecycleError,
} from './localchain';

type PowChallenge = {
    prefix: string;
    difficulty: number;
};

type NcInputState =
    | { kind: 'action' }
    | { kind: 'pow'; challenge: PowChallenge }
    | { kind: 'uuid'; action: 'flag' | 'kill' };

type NcServerOptions = {
    port: number;
    host?: string;
    flag: string;
};

const POW_DIFFICULTY = Number(process.env.POW_DIFFICULTY ?? '3');
const POW_PREFIX_BYTES = Number(process.env.POW_PREFIX_BYTES ?? '8');
const FUNC_IS_SOLVED = process.env.FUNC_IS_SOLVED ?? 'isSolved()';

function createPowChallenge(): PowChallenge {
    return {
        prefix: randomBytes(POW_PREFIX_BYTES).toString('hex'),
        difficulty: POW_DIFFICULTY,
    };
}

function verifyPow(challenge: PowChallenge, suffix: string) {
    const digest = createHash('sha256').update(challenge.prefix + suffix).digest('hex');
    return digest.startsWith('0'.repeat(challenge.difficulty));
}

function formatSession(session: LocalchainSessionView) {
    const lines = [
        '',
        `the instance will automatically terminate in ${Math.floor(session.timeToLive / 60000)} minutes`,
        "here's some useful information",
        `uuid: ${session.uuid}`,
        `challenge contract: ${session.challenge.address.toString()}`,
        `api v2: ${session.apiV2Endpoint}`,
        `your wallet version: ${session.player.version}`,
        `your wallet id: ${session.player.walletId}`,
        `seed: ${session.player.walletSeedHex}`,
    ];

    return `${lines.join('\n')}\n`;
}

function helpText() {
    return [
        '1. new  - launch new instance',
        `2. flag - get the flag (if ${FUNC_IS_SOLVED} is true)`,
        '3. kill - kill an instance',
    ].join('\n');
}

function mapError(error: unknown) {
    if (error instanceof SessionLifecycleError || error instanceof Error) {
        return error.message;
    }
    return 'unknown error';
}

export function startNcServer(options: NcServerOptions) {
    const server = net.createServer((socket) => {
        socket.setEncoding('utf8');

        let state: NcInputState = { kind: 'action' };
        let buffer = '';
        let busy = false;

        const promptAction = () => {
            socket.write('action? ');
        };

        const promptUuid = (action: 'flag' | 'kill') => {
            socket.write(`uuid? `);
        };

        const writeWelcome = () => {
            socket.write(`${helpText()}\n`);
            promptAction();
        };

        const writePowChallenge = (challenge: PowChallenge) => {
            const SOLVE_POW_SCRIPT = "https://gist.githubusercontent.com/YanhuiJessica/41872792ad6e97c9ddb186a5be6fd612/raw";
            socket.write(`\n== PoW ==\n`);
            socket.write(` sha256("${challenge.prefix}" + YOUR_INPUT) must start with ${challenge.difficulty} bytes zeros\n`);
            socket.write(' please run the following command to solve it:\n');
            socket.write(` python3 <(curl -sSL ${SOLVE_POW_SCRIPT}) ${challenge.prefix} ${challenge.difficulty}\n\n`);
            socket.write('YOUR_INPUT = ');
        };

        const createAndWriteSession = async () => {
            const session = await createLocalchainSession();
            socket.write(formatSession(session));
        };

        const handleActionInput = async (line: string) => {
            const [command] = line.trim().split(/\s+/).filter(Boolean);

            if (!command) {
                promptAction();
                return;
            }

            switch (command.toLowerCase()) {
                case 'new':
                case '1': {
                    if (POW_DIFFICULTY > 0) {
                        const challenge = createPowChallenge();
                        state = { kind: 'pow', challenge };
                        writePowChallenge(challenge);
                        return;
                    }

                    await createAndWriteSession();
                    socket.end();
                    return;
                }
                case 'flag':
                case '2': {
                    state = { kind: 'uuid', action: 'flag' };
                    promptUuid('flag');
                    return;
                }
                case 'kill':
                case '3': {
                    state = { kind: 'uuid', action: 'kill' };
                    promptUuid('kill');
                    return;
                }
                default: {
                    throw new Error('unknown');
                }
            }
        };

        const handlePowInput = async (line: string, challenge: PowChallenge) => {
            if (!verifyPow(challenge, line.trim())) {
                throw new Error('incorrect');
                return;
            }

            socket.write('correct\n');
            socket.write('== END POW ==\n');
            await createAndWriteSession();
            socket.end();
        };

        const handleUuidInput = async (line: string, action: 'flag' | 'kill') => {
            const uuid = line.trim();

            if (!uuid) {
                promptUuid(action);
                return;
            }

            if (action === 'flag') {
                const solved = await isChallengeSolved(uuid);
                if (!solved) {
                    throw new Error('not solved');
                }
                socket.write(`${options.flag}\n`);
            } else {
                await killLocalchainSession(uuid, 'manual');
                socket.write('killed\n');
            }

            socket.end();
        };

        socket.on('data', (chunk: string) => {
            buffer += chunk;

            while (buffer.includes('\n')) {
                const newlineIndex = buffer.indexOf('\n');
                const line = buffer.slice(0, newlineIndex).replace(/\r$/, '');
                buffer = buffer.slice(newlineIndex + 1);

                if (busy) {
                    socket.write('busy\n');
                    continue;
                }

                busy = true;

                void (async () => {
                    try {
                        switch (state.kind) {
                            case 'action':
                                await handleActionInput(line);
                                break;
                            case 'pow':
                                await handlePowInput(line, state.challenge);
                                break;
                            case 'uuid':
                                await handleUuidInput(line, state.action);
                                break;
                        }
                    } catch (error) {
                        socket.write(`${mapError(error)}\n`);
                        socket.destroy();
                        return;
                    } finally {
                        busy = false;
                    }
                })();
            }
        });

        socket.on('error', () => {
            socket.destroy();
            return;
        });
        writeWelcome();
    });

    server.listen(options.port, options.host ?? '0.0.0.0', () => {
        console.log(`NC server listening on ${options.host ?? '0.0.0.0'}:${options.port}`);
    });

    return server;
}