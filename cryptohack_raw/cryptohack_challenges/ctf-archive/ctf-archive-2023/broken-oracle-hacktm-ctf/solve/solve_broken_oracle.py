#!/usr/bin/env python3
import argparse
import math
import os
import random
import re
import socket
import sys
from dataclasses import dataclass
from typing import Optional, Tuple, List

# -------------------- number theory --------------------

def i2b(x: int) -> bytes:
    if x == 0:
        return b"\x00"
    return x.to_bytes((x.bit_length() + 7) // 8, "big")


def jacobi(a: int, n: int) -> int:
    a %= n
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be odd positive")
    j = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                j = -j
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            j = -j
        a %= n
    return j if n == 1 else 0


def crt(a: int, p: int, b: int, q: int) -> int:
    return (a + p * (((b - a) * pow(p, -1, q)) % q)) % (p * q)


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for p in small:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    # deterministic for small, very reliable for 1024-bit CTF primes
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def rand_prime_blum(bits: int) -> int:
    while True:
        x = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        # force p = 3 mod 4
        x += (3 - x) % 4
        if x.bit_length() == bits and is_probable_prime(x):
            return x

# -------------------- exact copy of server-side algorithms, no external deps --------------------

@dataclass
class Enc:
    r: int
    s: int
    t: int


def solve_quad_server(r: int, c: int, p: int) -> Tuple[int, int]:
    """Same algorithm as the challenge server."""
    r %= p
    c %= p

    def reduce_poly(poly: List[int]) -> None:
        if poly[2] == 0:
            return
        poly[1] = (poly[1] + poly[2] * r) % p
        poly[0] = (poly[0] - poly[2] * c) % p
        poly[2] = 0

    def prod(a: List[int], b: List[int]) -> List[int]:
        res = [
            a[0] * b[0] % p,
            (a[1] * b[0] + a[0] * b[1]) % p,
            a[1] * b[1] % p,
        ]
        reduce_poly(res)
        return res

    exp = (p - 1) // 2
    res = [1, 0, 0]
    cur = [0, 1, 0]
    while True:
        if exp & 1:
            res = prod(res, cur)
        exp >>= 1
        if exp == 0:
            break
        cur = prod(cur, cur)

    a1 = -(res[0] - 1) * pow(res[1], -1, p) % p
    a2 = (r - a1) % p
    return a1, a2


def encrypt_local(m: int, n: int, c: int) -> Enc:
    inv = pow(m, -1, n)
    cm = c * inv % n
    return Enc((m + cm) % n, jacobi(m, n), int(cm < m))


def decrypt_local(enc: Enc, p: int, q: int, c: int) -> int:
    n = p * q
    assert 0 <= enc.r < n
    assert enc.s in (1, -1)
    assert enc.t in (0, 1)
    mps = solve_quad_server(enc.r, c, p)
    mqs = solve_quad_server(enc.r, c, q)
    ms = []
    for mp in mps:
        for mq in mqs:
            m = crt(mp, p, mq, q)
            if jacobi(m, n) == enc.s:
                ms.append(m)
    assert len(ms) == 2
    ms.sort()
    return ms[1] if enc.t else ms[0]


class LocalOracle:
    def __init__(self, pbits: int = 96, flag: bytes = b"FAKEFLAG{LOCAL_TEST}"):
        self.p = rand_prime_blum(pbits)
        self.q = rand_prime_blum(pbits)
        while self.p == self.q:
            self.q = rand_prime_blum(pbits)
        self.n = self.p * self.q
        while True:
            self.c = random.randrange(1, self.n)
            if jacobi(self.c, self.p) == -1 and jacobi(self.c, self.q) == -1:
                break
        # same idea as the challenge, but keep it safely smaller for local tests
        m = int.from_bytes(flag + os.urandom(max(1, (self.n.bit_length() // 8) - len(flag) - 1)), "big")
        while not (0 < m < self.n and math.gcd(m, self.n) == 1):
            m = random.randrange(2, self.n)
        self.flag_plain = m
        self.enc_flag = encrypt_local(m, self.n, self.c)

    def query(self, r: int, s: int, t: int) -> Optional[Enc]:
        try:
            m = decrypt_local(Enc(r, s, t), self.p, self.q, self.c)
            return encrypt_local(m, self.n, self.c)
        except Exception:
            return None


class RemoteOracle:
    def __init__(self, host: str, port: int, timeout: float = 15.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        banner = self._recv_until(b"r, s, t = ")
        nums = list(map(int, re.findall(rb"(?:^|\n)(?:r|s|t) = (-?\d+)", banner)))
        if len(nums) < 3:
            raise RuntimeError("could not parse encrypted flag from banner:\n" + banner.decode(errors="replace"))
        self.enc_flag = Enc(nums[0], nums[1], nums[2])

    def _recv_until(self, token: bytes) -> bytes:
        data = b""
        while token not in data:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise EOFError("remote closed")
            data += chunk
        return data

    def query(self, r: int, s: int, t: int) -> Optional[Enc]:
        self.sock.sendall(f"{r},{s},{t}\n".encode())
        data = self._recv_until(b"r, s, t = ")
        if b"Something wrong" in data:
            return None
        nums = list(map(int, re.findall(rb"(?:^|\n)(?:r|s|t) = (-?\d+)", data)))
        if len(nums) < 3:
            return None
        return Enc(nums[0], nums[1], nums[2])

# -------------------- attack --------------------

def recover_c_mod_from_pair(r: int, y1: int, y2: int, mod: int) -> int:
    """
    In the prime where solve_quad is broken, it returns a,b with a+b=r.
    Oracle returns y1=a+c/a and y2=b+c/b.
    This gives a = r(r-y2)/(2r-y1-y2), then c=a(y1-a).
    """
    r %= mod
    y1 %= mod
    y2 %= mod
    den = (2 * r - y1 - y2) % mod
    a = (r * (r - y2) * pow(den, -1, mod)) % mod
    return (a * (y1 - a)) % mod


def query_record(oracle, r: int):
    outs = []
    for s in (-1, 1):
        for t in (0, 1):
            e = oracle.query(r, s, t)
            if e is not None:
                outs.append(e.r)
    uniq = sorted(set(outs))
    return uniq


def recover_key(oracle, min_factor_bits: int = 512, max_r: int = 80, verbose: bool = True):
    records = []  # (r, [two oracle r outputs]) for the useful exactly-one-prime-broken case
    diffs = []
    primes = []

    for r in range(1, max_r + 1):
        uniq = query_record(oracle, r)
        if verbose:
            print(f"[+] r={r}: {len(uniq)} distinct successful output(s)")
        if len(uniq) == 2:
            records.append((r, uniq))
            d = abs(uniq[1] - uniq[0])
            if d:
                for old in diffs:
                    g = math.gcd(d, old)
                    if g.bit_length() >= min_factor_bits and is_probable_prime(g):
                        if all(g != x for x in primes):
                            primes.append(g)
                            print(f"[+] recovered prime candidate ({g.bit_length()} bits)")
                diffs.append(d)

        if len(primes) >= 2:
            p, q = primes[0], primes[1]
            # Need c too; records collected so far are usually enough.
            c_p = c_q = None
            for rr, ys in records:
                y0, y1 = ys
                if c_p is None and (y0 - rr) % q == 0 and (y1 - rr) % q == 0 and (y0 - y1) % p != 0:
                    c_p = recover_c_mod_from_pair(rr, y0, y1, p)
                    print("[+] recovered c mod p")
                if c_q is None and (y0 - rr) % p == 0 and (y1 - rr) % p == 0 and (y0 - y1) % q != 0:
                    c_q = recover_c_mod_from_pair(rr, y0, y1, q)
                    print("[+] recovered c mod q")
                if c_p is not None and c_q is not None:
                    c = crt(c_p, p, c_q, q)
                    n = p * q
                    return p, q, n, c

    raise RuntimeError("failed to recover full key; increase --max-r")


def decrypt_flag(enc_flag: Enc, p: int, q: int, c: int) -> int:
    n = p * q
    r = enc_flag.r
    roots_p = solve_roots_valid(r, c, p)
    roots_q = solve_roots_valid(r, c, q)
    ms = []
    for mp in roots_p:
        for mq in roots_q:
            m = crt(mp, p, mq, q)
            if jacobi(m, n) == enc_flag.s:
                ms.append(m)
    assert len(ms) == 2, f"unexpected candidate count: {len(ms)}"
    ms.sort()
    return ms[1] if enc_flag.t else ms[0]


def solve_roots_valid(r: int, c: int, p: int) -> Tuple[int, int]:
    # For a genuine ciphertext, D is a square. p % 4 == 3.
    D = (r * r - 4 * c) % p
    sd = pow(D, (p + 1) // 4, p)
    inv2 = (p + 1) // 2
    return ((r + sd) * inv2 % p, (r - sd) * inv2 % p)


def clean_flag_bytes(b: bytes) -> bytes:
    # The server appends random bytes after the flag. Keep the normal CTF prefix up to the first closing brace.
    i = b.find(b"{")
    j = b.find(b"}", i + 1) if i != -1 else -1
    if i != -1 and j != -1:
        # include a likely prefix before the brace
        start = max(0, b.rfind(b"\x00", 0, i) + 1)
        return b[start:j + 1]
    return b


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    lp = sub.add_parser("local")
    lp.add_argument("--bits", type=int, default=96, help="prime bits for local test")
    lp.add_argument("--min-factor-bits", type=int, default=None)
    lp.add_argument("--max-r", type=int, default=80)
    rp = sub.add_parser("remote")
    rp.add_argument("host")
    rp.add_argument("port", type=int)
    rp.add_argument("--min-factor-bits", type=int, default=512)
    rp.add_argument("--max-r", type=int, default=80)
    args = ap.parse_args()

    if args.mode == "local":
        oracle = LocalOracle(args.bits)
        min_bits = args.min_factor_bits or max(16, args.bits - 8)
        print(f"[local] real p={oracle.p}")
        print(f"[local] real q={oracle.q}")
        print(f"[local] real c={oracle.c}")
    else:
        oracle = RemoteOracle(args.host, args.port)
        min_bits = args.min_factor_bits

    print(f"[+] encrypted flag: r={oracle.enc_flag.r}, s={oracle.enc_flag.s}, t={oracle.enc_flag.t}")
    p, q, n, c = recover_key(oracle, min_factor_bits=min_bits, max_r=args.max_r)
    print(f"[+] p = {p}")
    print(f"[+] q = {q}")
    print(f"[+] n = {n}")
    print(f"[+] c = {c}")

    m = decrypt_flag(oracle.enc_flag, p, q, c)
    pt = i2b(m)
    print(f"[+] plaintext bytes = {pt!r}")
    print(f"[+] flag = {clean_flag_bytes(pt)!r}")


if __name__ == "__main__":
    main()
