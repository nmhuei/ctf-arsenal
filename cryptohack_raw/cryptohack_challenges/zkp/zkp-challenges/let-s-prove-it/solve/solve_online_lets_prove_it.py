#!/usr/bin/env python3
import json
import socket
import re
import hashlib
import random
import string
from Crypto.Util.number import bytes_to_long, long_to_bytes, isPrime

HOST = "socket.cryptohack.org"
PORT = 13430
BITS = 2 << 9  # 1024
G = 2

def recv_until_json_or_banner(f):
    line = f.readline()
    if not line:
        raise EOFError("server closed connection")
    return line.decode(errors="replace").strip()

def send_json(f, obj):
    f.write((json.dumps(obj) + "\n").encode())
    f.flush()
    line = recv_until_json_or_banner(f)
    try:
        return json.loads(line)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Expected JSON, got: {line!r}") from e

def get_prime_from_seed(nonce: bytes, seed: bytes) -> int:
    R = random.Random(nonce + seed)
    while True:
        n = R.getrandbits(BITS) | 1
        if isPrime(n, randfunc=lambda x: long_to_bytes(R.getrandbits(x))):
            return n

def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def undo_xor_nonce(x: int, nonce: bytes) -> bytes:
    try:
        s = x.to_bytes(39, 'big')
    except OverflowError:
        s = long_to_bytes(x)
    return s[:7] + xor(s[7:-1], nonce) + s[-1:]

def strip_inserted_nonprintable(raw: bytes) -> bytes:
    for i, b in enumerate(raw):
        if chr(b) not in string.printable:
            cand = raw[:i] + raw[i + 1:]
            if cand.startswith(b"crypto{") and cand.endswith(b"}") and len(cand) == 38:
                return cand

    for i in range(len(raw)):
        cand = raw[:i] + raw[i + 1:]
        if cand.startswith(b"crypto{") and cand.endswith(b"}") and len(cand) == 38:
            return cand
    return raw

def main():
    with socket.create_connection((HOST, PORT), timeout=20) as sock:
        f = sock.makefile("rwb", buffering=0)
        banner_lines = []
        for _ in range(5):
            line = f.readline().decode(errors="replace").strip()
            if not line:
                break
            banner_lines.append(line)
            if "nonce" in line.lower() or any(len(part) == 62 for part in line.split()):
                break
        banner_text = "\n".join(banner_lines)
        print("[*] Banner received:")
        print(banner_text)

        m = re.search(r"([0-9a-f]{62})", banner_text)
        if not m:
            raise RuntimeError("Could not parse 31-byte nonce from banner")
        nonce = bytes.fromhex(m.group(1))
        print(f"[*] nonce = {nonce.hex()}")

        # 1. Burn first proof
        first = send_json(f, {"option": "get_proof"})
        if "error" in first:
            raise RuntimeError(first)
        print("[*] Burned first unknown-prime proof")

        # 2. Refresh with seed A
        seedA = b"A" * 8
        r = send_json(f, {"option": "refresh", "seed": seedA.hex()})
        if "error" in r:
            raise RuntimeError(r)
        print("[*] Seed A refreshed")

        # 3. Get proof 1 (known seed A)
        pr1 = send_json(f, {"option": "get_proof"})
        if "error" in pr1:
            raise RuntimeError(pr1)
        print("[*] Got proof 1")

        # Reconstruct prime
        p = get_prime_from_seed(nonce, seedA)

        # Calculate c
        t = pr1["t"]
        y = pr1["y"]
        r = pr1["r"]
        c = bytes_to_long(hashlib.sha3_256(long_to_bytes(t ^ y ^ G)).digest()) ** 2

        # Solve for FLAG range
        K = p - 1 - r
        flag_min = K // c
        flag_max = (K + (1 << 512)) // c

        print(f"[*] Searching FLAG candidates...")
        for x in range(flag_min - 5, flag_max + 5):
            raw = undo_xor_nonce(x, nonce)
            flag = strip_inserted_nonprintable(raw)
            if flag.startswith(b"crypto{") and flag.endswith(b"}"):
                print(f"[+] Found FLAG: {flag.decode()}")
                break

if __name__ == "__main__":
    main()
