#!/usr/bin/env python3
import argparse
import base64
import math
import random
import socket
import sys
from fractions import Fraction

B = 256
DOT = 46
E = 65537


def i2b(x: int) -> bytes:
    if x == 0:
        return b"\x00"
    return x.to_bytes((x.bit_length() + 7) // 8, "big")


def b2i(x: bytes) -> int:
    return int.from_bytes(x, "big")


class Remote:
    def __init__(self, host: str, port: int, timeout: float = 10.0):
        self.s = socket.create_connection((host, port), timeout=timeout)
        self.buf = b""
        self.recv_until(b"[cmd] ")

    def recv_until(self, token: bytes) -> bytes:
        while token not in self.buf:
            chunk = self.s.recv(4096)
            if not chunk:
                raise EOFError("connection closed")
            self.buf += chunk
        idx = self.buf.index(token) + len(token)
        out, self.buf = self.buf[:idx], self.buf[idx:]
        return out

    def cmd(self, line: str) -> str:
        self.s.sendall(line.encode() + b"\n")
        data = self.recv_until(b"[cmd] ")
        return data.decode(errors="replace")

    def get_n(self) -> int:
        out = self.cmd("pkey")
        for line in out.splitlines():
            if line.startswith("[pkey] "):
                return b2i(base64.b64decode(line.split(" ", 1)[1]))
        raise RuntimeError(f"could not parse public key from: {out!r}")

    def get_c(self) -> int:
        out = self.cmd("read")
        for line in out.splitlines():
            if line.startswith("[shhh] "):
                return b2i(base64.b64decode(line.split(" ", 1)[1]))
        raise RuntimeError(f"could not parse ciphertext from: {out!r}")

    def oracle_ct(self, ct: int) -> bool:
        payload = base64.b64encode(i2b(ct)).decode()
        out = self.cmd("send " + payload)
        return "nice" in out


def find_last_byte_candidates(oracle_s, limit: int = 512):
    """Recover m mod 256 candidates using small multipliers.

    The flag/message is much shorter than a 2048-bit modulus, so for small s
    we have s*m < n and the oracle checks (s*(m mod 256)) mod 256 == 46.
    For an odd final byte this leaves two candidates separated by 128.
    """
    observations = []
    for s in range(1, limit + 1):
        observations.append((s, oracle_s(s)))

    candidates = []
    for r in range(256):
        ok = True
        for s, ans in observations:
            if (((s * r) % B) == DOT) != ans:
                ok = False
                break
        if ok:
            candidates.append(r)
    return candidates


def recover_plaintext_integer(n: int, c: int, oracle_s, r: int, verbose: bool = True):
    """Recover m from an oracle for ((s*m mod n) & 0xff) == 46.

    Let alpha = m/n and q = floor(s*alpha).  Since
        s*m mod n = s*m - q*n,
    the low byte oracle is equivalent to
        q == ((s*r - 46) * n^{-1}) mod 256     (mod 256),
    where r = m mod 256.

    We choose s so that the accepted interval containing the current lower
    bound covers about half of the remaining interval, then update according
    to the oracle result.
    """
    inv_n = pow(n, -1, B)
    lo = Fraction(0, 1)
    hi = Fraction(1, 1)
    steps = 0

    while True:
        low_m = (lo.numerator * n + lo.denominator - 1) // lo.denominator
        high_m_excl = (hi.numerator * n + hi.denominator - 1) // hi.denominator
        remaining = high_m_excl - low_m
        if remaining <= 1:
            return low_m

        width = hi - lo
        target_s = max(1, (2 * width.denominator) // width.numerator)
        max_s = (B * width.denominator) // width.numerator - 1

        found = None
        # Expected ~128 tries when r is odd.  Keep a generous cap.
        for delta in range(0, 5000):
            if delta == 0:
                choices = (target_s,)
            else:
                choices = (target_s + delta, target_s - delta)
            for s in choices:
                if s <= 0 or s >= max_s:
                    continue
                q = (lo.numerator * s) // lo.denominator
                k = ((s * r - DOT) * inv_n) % B
                # Ensure lo is inside an accepted bucket, the bucket ends
                # before hi, and no second accepted bucket can occur in [lo, hi).
                if q % B == k:
                    end = Fraction(q + 1, s)
                    if lo < end < hi and Fraction(q + B, s) >= hi:
                        found = (s, end)
                        break
            if found is not None:
                break

        # Fallback to random search to bypass periodic rational approximation traps
        if found is None:
            s_min = int(Fraction(11, 10) / width) + 1
            s_max = int(Fraction(254, 1) / width)
            if s_max > s_min:
                for _ in range(100000):
                    s = random.randint(s_min, s_max)
                    q = (lo.numerator * s) // lo.denominator
                    k = ((s * r - DOT) * inv_n) % B
                    if q % B == k:
                        end = Fraction(q + 1, s)
                        if lo < end < hi and Fraction(q + B, s) >= hi:
                            found = (s, end)
                            break

        if found is None:
            raise RuntimeError("failed to find a splitting multiplier")

        s, end = found
        if oracle_s(s):
            hi = end
        else:
            lo = end

        steps += 1
        if verbose and steps % 128 == 0:
            bits_left = max(0.0, math.log2(remaining))
            print(f"[+] step {steps:4d}, about {bits_left:.1f} candidate bits left", file=sys.stderr)


def solve_remote(host: str, port: int, verbose: bool = True):
    io = Remote(host, port)
    n = io.get_n()
    c = io.get_c()
    print(f"[+] n bits = {n.bit_length()}", file=sys.stderr)

    def oracle_s(s: int) -> bool:
        return io.oracle_ct((c * pow(s, E, n)) % n)

    candidates = find_last_byte_candidates(oracle_s)
    print(f"[+] final-byte candidates: {[hex(x) for x in candidates]}", file=sys.stderr)

    # CryptoHack flags normally end with '}', so try that candidate first.
    candidates = sorted(candidates, key=lambda x: x != ord("}"))

    for r in candidates:
        print(f"[+] trying r = {r:#04x}", file=sys.stderr)
        try:
            m = recover_plaintext_integer(n, c, oracle_s, r, verbose=verbose)
            if pow(m, E, n) == c:
                msg = i2b(m)
                print(msg.decode(errors="replace"))
                return msg
        except Exception as e:
            print(f"[-] candidate r = {r:#04x} failed: {e}", file=sys.stderr)
        print(f"[-] candidate r = {r:#04x} failed ciphertext check", file=sys.stderr)
    raise RuntimeError("no candidate recovered a valid plaintext")


def local_self_test():
    # This tests the interval/oracle attack math without needing PyCryptodome.
    n = random.getrandbits(2048) | (1 << 2047) | 1
    m = b2i(b"crypto{local_self_test_flag}")
    assert m < n

    def oracle_s(s: int) -> bool:
        return ((s * m) % n) % B == DOT

    r = m % B
    rec = recover_plaintext_integer(n, 0, oracle_s, r, verbose=False)
    print(i2b(rec).decode())
    assert rec == m
    print("self-test ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("host", nargs="?", default="archive.cryptohack.org")
    ap.add_argument("port", nargs="?", type=int, default=53580)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        local_self_test()
    else:
        solve_remote(args.host, args.port, verbose=not args.quiet)


if __name__ == "__main__":
    main()
