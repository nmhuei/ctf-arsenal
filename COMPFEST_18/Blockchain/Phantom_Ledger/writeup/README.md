# Writeup: Phantom Ledger

| Property | Value |
| :--- | :--- |
| **Category** | `Blockchain` |
| **Points** | `100` |
| **Author** | `Aero` |
| **Solves** | `59` |

---

## 📝 Challenge Overview

```
A cutting-edge DeFi vault called PhantomVault has been deployed to the blockchain.
It supports gasless meta-transactions, allowing users to deposit ETH and authorize withdrawals through signed messages — submitted by a trusted relayer on their behalf.

The vault holds 10 ETH belonging to the protocol. Your mission: drain it.
```

Portal: `http://34.2.147.230:8502/`

---

## 🔍 Phân tích & Lỗ hổng

### 1. Phân tích Smart Contract (`Setup.sol` & `PhantomVault.sol`)
* Trong `Setup.sol`:
  ```solidity
  constructor(address _player) payable {
      vault = new PhantomVault{value: msg.value}(_player, _player);
  }
  ```
  * `Setup` deploy `PhantomVault` với `10 ETH`.
  * `owner = address(Setup)`.
  * `relayer = _player` và `feeRecipient = _player`.
  * `balances[owner] = 10 ETH`, `balances[player] = 0`.

* Trong `PhantomVault.sol`:
  ```solidity
  function transferCredit(address from, address to, uint256 amount) external {
      require(msg.sender == from || msg.sender == relayer, "Not authorized");
      require(balances[from] >= amount, "Insufficient credit");

      balances[from] -= amount;
      balances[to] += amount;

      emit CreditTransfer(from, to, amount);
  }
  ```
  * Hàm `transferCredit` cho phép `msg.sender == relayer` chuyển credit từ **BẤT KỲ** địa chỉ nào (`from`) sang địa chỉ khác (`to`).
  * Vì `player` chính là `relayer`, `player` có quyền chuyển toàn bộ 10 ETH số dư của `owner` (`Setup`) sang tài khoản của chính mình.

### 2. Kịch bản khai thác (Exploit Steps)
1. Giải PoW (`pwn.red/pow`) và khởi chạy blockchain instance qua portal API (`/solution` -> `/launch`).
2. Lấy thông tin RPC, player private key và địa chỉ `Setup`.
3. Gọi `vault.transferCredit(owner, player, 10 ether)`: Chuyển toàn bộ 10 ETH balance từ `Setup` sang `player`.
4. Gọi `vault.withdraw(10 ether)`: Rút toàn bộ ETH từ `PhantomVault` về ví `player`.
5. Số dư của `PhantomVault` trở về `0` ➔ `Setup.isSolved()` trả về `true`.
6. Gọi `GET /flag` từ portal API lấy flag.

---

## 💻 Script khai thác

Script tự động giải PoW, deploy instance, tương tác web3 và lấy flag tại [`../solver/solve.py`](../solver/solve.py).

```bash
python3 solver/solve.py
```

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `COMPFEST18{ph4nt0m_l3dg3r_cr0ss_funct10n_r33ntr4ncy_w1th_ecdsa_m4ll3ab1l1ty}`
