#!/usr/bin/env python3
import json
import socket
import re
import hashlib
import random
import string
from Crypto.Util.number import bytes_to_long, long_to_bytes, isPrime

HOST = "socket.cryptohack.org"
PORT = 13431
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

def c_candidates(t: int, y: int):
    out = []
    for z in range(2, BITS + 1):
        c = bytes_to_long(hashlib.sha3_256(long_to_bytes(t ^ y ^ G ^ z)).digest())
        out.append(c)
    return out

def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def undo_xor_nonce(x: int, nonce: bytes) -> bytes:
    s = long_to_bytes(x, 39)
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

        # 4. Get proof 2 (unknown seed, but needed to increment your_turn)
        pr2 = send_json(f, {"option": "get_proof"})
        if "error" in pr2:
            raise RuntimeError(pr2)
        print("[*] Got proof 2 (unknown seed)")

        # 5. Refresh with seed B
        seedB = b"B" * 8
        r = send_json(f, {"option": "refresh", "seed": seedB.hex()})
        if "error" in r:
            raise RuntimeError(r)
        print("[*] Seed B refreshed")

        # 6. Get proof 3 (known seed B)
        pr3 = send_json(f, {"option": "get_proof"})
        if "error" in pr3:
            raise RuntimeError(pr3)
        print("[*] Got proof 3")

        # Reconstruct primes
        p1 = get_prime_from_seed(nonce, seedA)
        p3 = get_prime_from_seed(nonce, seedB)

        # Generate candidate c lists
        cs1 = c_candidates(pr1["t"], pr1["y"])
        cs3 = c_candidates(pr3["t"], pr3["y"])

        r1 = pr1["r"]
        r3 = pr3["r"]
        m1 = p1 - 1
        m3 = p3 - 1

        # Determine k1 and k3
        k1 = 0 if r1 < (1 << 900) else 1
        k3 = 0 if r3 < (1 << 900) else 1

        # RHS = (r3 - k3 * m3) - (r1 - k1 * m1)
        rhs = (r3 - k3 * m3) - (r1 - k1 * m1)

        print("[*] Starting optimized solver loop...")
        found = False
        target_high = bytes_to_long(b"crypto{")
        x_min = target_high << 256
        x_max = (target_high + 1) << 256

        for c1 in cs1:
            for c3 in cs3:
                den = c1 - c3
                if den == 0:
                    continue
                if rhs % den != 0:
                    continue
                x = rhs // den
                if x_min <= x < x_max:
                    raw = undo_xor_nonce(x, nonce)
                    flag = strip_inserted_nonprintable(raw)
                    if flag.startswith(b"crypto{") and flag.endswith(b"}"):
                        print(f"[+] Found FLAG: {flag.decode()}")
                        found = True
                        break
            if found:
                break

if __name__ == "__main__":
    main()
