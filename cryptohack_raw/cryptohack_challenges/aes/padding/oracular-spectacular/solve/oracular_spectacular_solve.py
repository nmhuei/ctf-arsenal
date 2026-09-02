#!/usr/bin/env python3
"""
CryptoHack - Oracular Spectacular solver

Local test:
    python3 oracular_spectacular_solve.py --local

Remote:
    python3 oracular_spectacular_solve.py --remote --host socket.cryptohack.org --port 13423

The oracle is noisy:
    valid padding   -> result True with probability 0.4
    invalid padding -> result True with probability 0.6
So a False response is evidence that the tested padding candidate is correct.
"""
import argparse
import json
import math
import os
import random
import socket
import sys
from typing import Callable, Optional

HEX = b"0123456789abcdef"
LOG_TRUE = math.log(0.4 / 0.6)    # True response: candidate is less likely valid
LOG_FALSE = math.log(0.6 / 0.4)   # False response: candidate is more likely valid


def logsumexp(xs):
    m = max(xs)
    return m + math.log(sum(math.exp(x - m) for x in xs))


def top_confidence(logp, threshold: float):
    top = max(range(16), key=lambda i: logp[i])
    rest = [logp[i] for i in range(16) if i != top]
    gap = logp[top] - logsumexp(rest)
    return gap > math.log(threshold / (1.0 - threshold)), top


class RemoteChallenge:
    def __init__(self, host: str, port: int, timeout: float = 10.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.file = self.sock.makefile("rwb", buffering=0)
        self.queries = 0
        # Banner line, usually not JSON.
        try:
            self.file.readline()
        except Exception:
            pass

    def _send(self, obj):
        self.file.write(json.dumps(obj).encode() + b"\n")
        line = self.file.readline()
        if not line:
            raise EOFError("server closed the connection")
        return json.loads(line.decode())

    def encrypt(self) -> bytes:
        r = self._send({"option": "encrypt"})
        if "ct" not in r:
            raise RuntimeError(f"bad encrypt response: {r}")
        return bytes.fromhex(r["ct"])

    def unpad(self, ct: bytes) -> bool:
        self.queries += 1
        r = self._send({"option": "unpad", "ct": ct.hex()})
        if "result" not in r:
            raise RuntimeError(f"bad oracle response: {r}")
        return bool(r["result"])

    def check(self, msg: str):
        return self._send({"option": "check", "message": msg})

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


# A faithful local simulator. Remote mode does not need cryptography.
def pkcs7_unpad_ok(data: bytes, block_size: int = 16) -> bool:
    if not data or len(data) % block_size != 0:
        return False
    n = data[-1]
    return 1 <= n <= block_size and data[-n:] == bytes([n]) * n


class LocalChallenge:
    def __init__(self):
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        except ImportError as exc:
            raise SystemExit("Local mode needs: pip install cryptography") from exc
        self.Cipher = Cipher
        self.algorithms = algorithms
        self.modes = modes
        self.message = os.urandom(16).hex()
        self.key = os.urandom(16)
        self.queries = 0
        self.max_queries = 12_000

    def _aes_cbc_encrypt(self, iv: bytes, pt: bytes) -> bytes:
        enc = self.Cipher(self.algorithms.AES(self.key), self.modes.CBC(iv)).encryptor()
        return enc.update(pt) + enc.finalize()

    def _aes_cbc_decrypt(self, iv: bytes, ct: bytes) -> bytes:
        dec = self.Cipher(self.algorithms.AES(self.key), self.modes.CBC(iv)).decryptor()
        return dec.update(ct) + dec.finalize()

    def encrypt(self) -> bytes:
        iv = os.urandom(16)
        return iv + self._aes_cbc_encrypt(iv, self.message.encode())

    def unpad(self, ct: bytes) -> bool:
        if self.queries >= self.max_queries:
            raise RuntimeError("local query limit reached")
        iv, body = ct[:16], ct[16:]
        good = pkcs7_unpad_ok(self._aes_cbc_decrypt(iv, body), 16)
        self.queries += 1
        return good ^ (random.random() > 0.4)

    def check(self, msg: str):
        if msg == self.message:
            return {"flag": "crypto{local_simulator_success}"}
        return {"error": "incorrect message", "real_message": self.message}


class Budget:
    def __init__(self, max_queries: int = 11_950):
        self.max_queries = max_queries
        self.used = 0

    def left(self) -> int:
        return self.max_queries - self.used

    def note(self):
        self.used += 1


def recover_block(prev: bytes, cur: bytes, oracle: Callable[[bytes], bool],
                  budget: Budget, remaining_positions_cb: Callable[[], int],
                  threshold: float = 0.999, label: str = "") -> bytes:
    recovered = bytearray(16)

    for pos in range(15, -1, -1):
        pad = 16 - pos
        logp = [0.0] * 16
        local_queries = 0

        while True:
            ok, top = top_confidence(logp, threshold)
            if ok and local_queries > 0:
                break

            # Keep a small reserve for the remaining unknown bytes. If a byte is
            # unusually unlucky, take the current MAP candidate and let check()
            # reject the whole attempt if needed.
            reserve = remaining_positions_cb() * 70 + 10
            if budget.left() <= reserve or local_queries >= 1400:
                break

            guess = HEX[top]
            mod = bytearray(prev)
            for j in range(pos + 1, 16):
                mod[j] = prev[j] ^ recovered[j] ^ pad
            mod[pos] = prev[pos] ^ guess ^ pad

            result = oracle(bytes(mod) + cur)
            budget.note()
            local_queries += 1
            logp[top] += LOG_TRUE if result else LOG_FALSE

        _, top = top_confidence(logp, 0.5)
        recovered[pos] = HEX[top]
        sys.stderr.write(f"{label}[{pos:02d}] = {chr(recovered[pos])}  ({local_queries} oracle calls)\n")

    return bytes(recovered)


def solve_session(chal, threshold: float = 0.999) -> str:
    ct = chal.encrypt()
    if len(ct) != 48:
        raise RuntimeError(f"unexpected ciphertext length {len(ct)}")
    iv, c1, c2 = ct[:16], ct[16:32], ct[32:48]

    budget = Budget(11_950)
    positions_left = 32

    def oracle(x: bytes) -> bool:
        return chal.unpad(x)

    def rem():
        return positions_left

    p1 = recover_block(iv, c1, oracle, budget, rem, threshold, "P1")
    positions_left -= 16
    p2 = recover_block(c1, c2, oracle, budget, rem, threshold, "P2")
    positions_left -= 16
    return (p1 + p2).decode("ascii")


def run_local(args):
    for attempt in range(1, args.attempts + 1):
        chal = LocalChallenge()
        try:
            msg = solve_session(chal, args.threshold)
            r = chal.check(msg)
        except Exception as exc:
            print(f"attempt {attempt}: failed with {exc}")
            continue
        print(f"attempt {attempt}: queries={chal.queries} message={msg}")
        print(r)
        if "flag" in r:
            return
    raise SystemExit("No successful local attempt; increase --attempts or lower/raise --threshold.")


def run_remote(args):
    for attempt in range(1, args.attempts + 1):
        chal: Optional[RemoteChallenge] = None
        try:
            chal = RemoteChallenge(args.host, args.port)
            msg = solve_session(chal, args.threshold)
            r = chal.check(msg)
            print(f"attempt {attempt}: queries={chal.queries} message={msg}")
            print(r)
            if "flag" in r:
                return
        except Exception as exc:
            print(f"attempt {attempt}: failed with {exc}", file=sys.stderr)
        finally:
            if chal:
                chal.close()
    raise SystemExit("No flag received; rerun with more --attempts.")


def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--local", action="store_true")
    mode.add_argument("--remote", action="store_true")
    ap.add_argument("--host", default="socket.cryptohack.org")
    ap.add_argument("--port", type=int, default=13423)
    ap.add_argument("--attempts", type=int, default=10)
    ap.add_argument("--threshold", type=float, default=0.999)
    args = ap.parse_args()

    if args.local:
        run_local(args)
    else:
        run_remote(args)


if __name__ == "__main__":
    main()
