#!/usr/bin/env python3
"""
Solver for CryptoHack CTF Archive: RSA Permutation (WACON)

Usage:
  python3 solve_rsa_permutation.py --self-test --bits 1024
  python3 solve_rsa_permutation.py archive.cryptohack.org 45400
"""

import argparse
import hashlib
import random
import secrets
import socket
import sys
import time

E = 293
HEX = "0123456789abcdef"


def recover_factors(n: int, a: str, b: str, e: int = E):
    """Recover p, q from n and the two permuted hex encodings of dp, dq."""
    L = len(a)
    ar = [int(c, 16) for c in a[::-1]]  # least significant displayed nibbles first
    br = [int(c, 16) for c in b[::-1]]
    all_values = range(16)
    odd_values = [1, 3, 5, 7, 9, 11, 13, 15]

    # If e*dp - 1 = kp*(p-1), then e*dp + kp - 1 = kp*p.
    # Reducing modulo e gives p = 1 - kp^-1 (mod e). Same for q.
    # This turns ~292^2 key multiplier pairs into ~292 candidates.
    pairs = []
    n_mod_e = n % e
    for kp in range(2, e):
        p_mod = (1 - pow(kp, -1, e)) % e
        if p_mod == 0:
            continue
        q_mod = n_mod_e * pow(p_mod, -1, e) % e
        if q_mod == 0:
            continue
        denom = (1 - q_mod) % e
        if denom == 0:
            continue
        kq = pow(denom, -1, e)
        if 1 <= kq < e:
            pairs.append((kp, kq))

    c0, d0 = ar[0], br[0]

    for kp, kq in pairs:
        target0 = (kp * kq * n) & 0xF
        first_nibble_options = []

        # dp and dq must be odd because e*dp == 1 mod 2 and e*dq == 1 mod 2.
        for x in odd_values:
            for y in odd_values:
                if c0 == d0 and x != y:
                    continue
                if c0 != d0 and x == y:
                    continue
                left = (e * x + kp - 1) * (e * y + kq - 1)
                if ((left - target0) & 0xF) == 0:
                    first_nibble_options.append((x, y))

        if not first_nibble_options:
            continue

        full_target = kp * kq * n

        def dfs(i, mapping, used_mask, d1_low, d2_low):
            if i == L:
                X = e * d1_low + kp - 1
                Y = e * d2_low + kq - 1
                if X % kp == 0 and Y % kq == 0:
                    p = X // kp
                    q = Y // kq
                    if 1 < p < n and 1 < q < n and p * q == n:
                        return p, q
                return None

            ca, cb = ar[i], br[i]
            va_known, vb_known = mapping[ca], mapping[cb]
            candidates = []

            if va_known != -1 and vb_known != -1:
                candidates.append((va_known, vb_known, False, False))
            elif ca == cb:
                if va_known != -1:
                    candidates.append((va_known, va_known, False, False))
                else:
                    for v in all_values:
                        if not ((used_mask >> v) & 1):
                            candidates.append((v, v, True, True))
            elif va_known != -1:
                for v in all_values:
                    if not ((used_mask >> v) & 1) and v != va_known:
                        candidates.append((va_known, v, False, True))
            elif vb_known != -1:
                for v in all_values:
                    if not ((used_mask >> v) & 1) and v != vb_known:
                        candidates.append((v, vb_known, True, False))
            else:
                remaining = [v for v in all_values if not ((used_mask >> v) & 1)]
                for va in remaining:
                    for vb in remaining:
                        if va != vb:
                            candidates.append((va, vb, True, True))

            shift = 4 * i
            nibble_weight = 1 << shift
            modulus = 1 << (4 * (i + 1))
            target = full_target & (modulus - 1)

            for va, vb, new_a, new_b in candidates:
                nd1 = d1_low + va * nibble_weight
                nd2 = d2_low + vb * nibble_weight
                X = (e * nd1 + kp - 1) & (modulus - 1)
                Y = (e * nd2 + kq - 1) & (modulus - 1)

                if ((X * Y - target) & (modulus - 1)) != 0:
                    continue

                next_mapping = mapping
                next_used = used_mask
                if new_a or new_b:
                    next_mapping = mapping.copy()
                    if new_a:
                        next_mapping[ca] = va
                        next_used |= 1 << va
                    if new_b:
                        next_mapping[cb] = vb
                        next_used |= 1 << vb

                result = dfs(i + 1, next_mapping, next_used, nd1, nd2)
                if result:
                    return result

            return None

        for x, y in first_nibble_options:
            mapping = [-1] * 16  # displayed nibble -> real nibble
            if c0 == d0:
                mapping[c0] = x
                used = 1 << x
                d1 = d2 = x
            else:
                mapping[c0] = x
                mapping[d0] = y
                used = (1 << x) | (1 << y)
                d1, d2 = x, y

            result = dfs(1, mapping, used, d1, d2)
            if result:
                return result

    raise RuntimeError("failed to recover factors")


def solve_pow(prefix: str) -> str:
    i = 0
    while True:
        answer = str(i)
        if hashlib.sha256((prefix + answer).encode()).hexdigest().startswith("000000"):
            return answer
        i += 1


class Remote:
    def __init__(self, host: str, port: int, timeout: int = 60):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.file = self.sock.makefile("rwb", buffering=0)

    def readline(self) -> str:
        line = self.file.readline()
        if not line:
            raise EOFError("remote closed the connection")
        text = line.decode(errors="replace").strip()
        print("<<", text)
        return text

    def sendline(self, value):
        data = str(value).encode()
        print(">>", data.decode(errors="replace"))
        self.file.write(data + b"\n")

    def close(self):
        self.sock.close()


def solve_remote(host: str, port: int):
    io = Remote(host, port)
    try:
        io.readline()      # Solve PoW plz
        prefix = io.readline()

        t = time.time()
        pow_answer = solve_pow(prefix)
        print(f"[+] PoW solved in {time.time() - t:.2f}s")
        io.sendline(pow_answer)

        n = int(io.readline())
        a = io.readline()
        b = io.readline()

        t = time.time()
        p, q = recover_factors(n, a, b)
        print(f"[+] factors recovered in {time.time() - t:.2f}s")
        io.sendline(p)
        io.sendline(q)

        io.sock.settimeout(5)
        while True:
            try:
                line = io.file.readline()
                if not line:
                    break
                print("<<", line.decode(errors="replace").rstrip())
            except Exception:
                break
    finally:
        io.close()


# Small dependency-free local test generator. The challenge uses strong primes, but
# the exploit only needs primes p, q with (p-1) and (q-1) not divisible by e.
def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for p in small_primes:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    # Enough for a CTF self-test; this is probabilistic for large n.
    bases = small_primes + [secrets.randbelow(n - 3) + 2 for _ in range(8)]
    for a in bases:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def random_prime(bits: int) -> int:
    while True:
        n = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if (n - 1) % E != 0 and is_probable_prime(n):
            return n


def self_test(bits: int):
    p = random_prime(bits)
    q = random_prime(bits)
    while p == q:
        q = random_prime(bits)

    n = p * q
    dp = pow(E, -1, p - 1)
    dq = pow(E, -1, q - 1)
    byte_len = (bits + 7) // 8

    perm = list(HEX)
    random.shuffle(perm)

    def mapped(hex_string: str) -> str:
        return "".join(perm[int(c, 16)] for c in hex_string)

    a = mapped(dp.to_bytes(byte_len, "big").hex())
    b = mapped(dq.to_bytes(byte_len, "big").hex())

    t = time.time()
    rp, rq = recover_factors(n, a, b)
    elapsed = time.time() - t
    ok = {rp, rq} == {p, q}
    print(f"self-test bits={bits}: ok={ok}, recovered in {elapsed:.3f}s")
    if not ok:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", nargs="?", default="archive.cryptohack.org")
    parser.add_argument("port", nargs="?", type=int, default=45400)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--bits", type=int, default=256, help="prime size for --self-test")
    args = parser.parse_args()

    if args.self_test:
        self_test(args.bits)
    else:
        solve_remote(args.host, args.port)


if __name__ == "__main__":
    main()
