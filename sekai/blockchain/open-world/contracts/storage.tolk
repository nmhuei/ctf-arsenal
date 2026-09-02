
struct WalletStorage {
    jettonBalance: coins
    ownerAddress: address
    minterAddress: address
}

struct MinterStorage {
    totalSupply: coins
    adminAddress: address
    content: cell
    jettonWalletCode: cell
}

struct ChallengeStorage {
    remainingPlayerBonus: uint8
    player: address
    minter: address?
    wallet: address?
    isSolved: bool
}


fun MinterStorage.load() {
    return MinterStorage.fromCell(contract.getData())
}

fun MinterStorage.save(self) {
    contract.setData(self.toCell())
}


fun WalletStorage.load() {
    return WalletStorage.fromCell(contract.getData())
}

fun WalletStorage.save(self) {
    contract.setData(self.toCell())
}

fun ChallengeStorage.load() {
    return ChallengeStorage.fromCell(contract.getData())
}

fun ChallengeStorage.save(self) {
    contract.setData(self.toCell())
}