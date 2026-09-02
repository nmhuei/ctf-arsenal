import { OpenedContract, Sender } from "@ton/core";
import { WalletContractV3R2 } from "@ton/ton";

export type WalletContext = {
    wallet: OpenedContract<WalletContractV3R2>;
    sender: Sender;
};