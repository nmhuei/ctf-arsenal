import "@gen/JettonMinter.code.tolk"
import "@gen/JettonWallet.code.tolk"
import "@contracts/storage"
import "@contracts/messages"
import "@contracts/errors"

contract Challenge {
    storage: ChallengeStorage
    incomingMessages: AllowedMessageToChallenge
}

type AllowedMessageToChallenge =
    | SetupChallenge
    | PlayerBonus
    | Buy
    | TransferNotificationForRecipient
    | ResponseWalletAddress

type ChallengeForwardPayload =
    | Sell
    | Solve

const TOKEN_PRICE: coins = ton("2")
const FLAG_PRICE: coins = 100
const BUY_MINT_TON_AMOUNT: coins = ton("0.12")

fun onInternalMessage(in: InMessage) {
    val msg = lazy AllowedMessageToChallenge.fromSlice(in.body);

    match (msg) {
        SetupChallenge => {
            var storage = lazy ChallengeStorage.load();
            assert (storage.minter == null) throw Errors.CHALLENGE_INITIALIZED;

            val minterInit = ContractState {
                code: jettonMinterCompiledCode(),
                data: MinterStorage {
                    totalSupply: 0,
                    adminAddress: contract.getAddress(),
                    content: createEmptyCell(),
                    jettonWalletCode: jettonWalletCompiledCode()
                }.toCell()
            };
            storage.minter = AutoDeployAddress { stateInit: minterInit }.calculateAddress();
            storage.save();

            val deployMsg = createMessage({
                bounce: false,
                dest: { stateInit: minterInit},
                value: ton("0.5")
            });
            deployMsg.send(SEND_MODE_REGULAR);
            val requestWalletMsg = createMessage({
                bounce: false,
                dest: storage.minter,
                value: ton("0.1"),
                body: RequestWalletAddress {
                    queryId: 0,
                    ownerAddress: contract.getAddress(),
                    includeOwnerAddress: false
                }
            });
            requestWalletMsg.send(SEND_MODE_REGULAR);
        }
        PlayerBonus => {
            var storage = lazy ChallengeStorage.load();
            assert (storage.minter != null) throw Errors.CHALLENGE_NOT_INITIALIZED;
            val hasBonus = storage.remainingPlayerBonus != 0;

            storage.remainingPlayerBonus -= 1;
            storage.save();

            if (hasBonus) {
                val mintMsg = createMessage({
                    bounce: false,
                    dest: storage.minter!,
                    value: 0,
                    body: MintNewJettons {
                        queryId: 0,
                        mintRecipient: in.senderAddress,
                        tonAmount: ton("0.1"),
                        internalTransferMsg: InternalTransferStep {
                            queryId: 0,
                            jettonAmount: FLAG_PRICE / 2,
                            transferInitiator: null,
                            sendExcessesTo: null,
                            forwardTonAmount: 0,
                            forwardPayload: createEmptySlice()
                        }.toCell()
                    }
                });
                mintMsg.send(SEND_MODE_CARRY_ALL_REMAINING_MESSAGE_VALUE);
            }
        }
        Buy => {
            val storage = lazy ChallengeStorage.load();
            assert (storage.minter != null) throw Errors.CHALLENGE_NOT_INITIALIZED;
            assert (
                in.valueCoins > msg.amount * TOKEN_PRICE + BUY_MINT_TON_AMOUNT
            ) throw Errors.INSUFFICIENT_FUNDS;

            val mintMsg = createMessage({
                bounce: false,
                dest: storage.minter!,
                value: BUY_MINT_TON_AMOUNT,
                body: MintNewJettons {
                    queryId: 0,
                    mintRecipient: in.senderAddress,
                    tonAmount: ton("0.1"),
                    internalTransferMsg: InternalTransferStep {
                        queryId: 0,
                        jettonAmount: msg.amount,
                        transferInitiator: null,
                        sendExcessesTo: null,
                        forwardTonAmount: 0,
                        forwardPayload: createEmptySlice(),
                    }.toCell(),
                },
            });
            mintMsg.send(SEND_MODE_REGULAR);

            reserveToncoinsOnBalance(msg.amount * TOKEN_PRICE, RESERVE_MODE_INCREASE_BY_ORIGINAL_BALANCE);
            val refundMsg = createMessage({
                bounce: false,
                dest: in.senderAddress,
                value: 0,
                body: ReturnExcessesBack { queryId: 0 },
            });
            refundMsg.send(SEND_MODE_CARRY_ALL_BALANCE); 
        }
        TransferNotificationForRecipient => {
            var storage = lazy ChallengeStorage.load();
            assert (storage.wallet != null) throw Errors.CHALLENGE_NOT_INITIALIZED;
            assert (in.senderAddress == storage.wallet) throw Errors.INVALID_CALLER;
            val payload = lazy ChallengeForwardPayload.fromSlice(msg.forwardPayload);

            match (payload) {
                Sell => {
                    if (msg.transferInitiator != null && msg.jettonAmount > 0) {
                        val payoutMsg = createMessage({
                            bounce: false,
                            dest: msg.transferInitiator!,
                            value: msg.jettonAmount * TOKEN_PRICE,
                            body: Payout {}
                        });
                        payoutMsg.send(SEND_MODE_CARRY_ALL_REMAINING_MESSAGE_VALUE);
                    }
                }
                Solve => {
                    if (msg.transferInitiator != null && storage.player == msg.transferInitiator!) {
                        if (msg.jettonAmount >= FLAG_PRICE) {
                            storage.isSolved = true;
                            storage.save();
                        }
                    }
                }
                else => {
                    assert (in.body.isEmpty()) throw 0xFFFF;
                }
            }
        }
        ResponseWalletAddress => {
            var storage = lazy ChallengeStorage.load();
            assert (storage.minter != null) throw Errors.CHALLENGE_NOT_INITIALIZED;
            assert (in.senderAddress == storage.minter) throw Errors.INVALID_CALLER;

            storage.wallet = msg.jettonWalletAddress;
            storage.save();
        }
        else => {
            assert (in.body.isEmpty()) throw 0xFFFF;
        }
    }
}

get fun minter(): address {
    val storage = lazy ChallengeStorage.load();
    assert (storage.minter != null) throw Errors.CHALLENGE_NOT_INITIALIZED;
    return storage.minter!;
}

get fun isSolved(): bool {
    val storage = lazy ChallengeStorage.load();
    return storage.isSolved;
}