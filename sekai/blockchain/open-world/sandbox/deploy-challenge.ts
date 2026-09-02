import { Address } from '@ton/core';
import { TonClient } from '@ton/ton';
import { Challenge } from '../wrappers-ts/Challenge.gen';
import { WalletContext } from './types';

export type ChallengeDeployment = {
    address: Address;
    nonce: bigint;
};

export async function deployChallengeInstance(client: TonClient, deployer: WalletContext, player: WalletContext, deployValue: bigint): Promise<ChallengeDeployment> {
    const challenge = Challenge.fromStorage({
        remainingPlayerBonus: 2n,
        player: player.wallet.address,
        minter: null,
        wallet: null,
        isSolved: false,
    });

    const currentSeqno = await deployer.wallet.getSeqno();
    const provider = client.provider(challenge.address, challenge.init);

    await provider.internal(deployer.sender, {
        value: deployValue,
        body: Challenge.createCellOfSetupChallenge({}),
    });

    return {
        address: challenge.address,
        nonce: BigInt(currentSeqno),
    };
}

export async function isChallengeInstanceSolved(client: TonClient, addr: Address): Promise<boolean> {
    const challenge = client.open(Challenge.fromAddress(addr));
    return challenge.getIsSolved();
}