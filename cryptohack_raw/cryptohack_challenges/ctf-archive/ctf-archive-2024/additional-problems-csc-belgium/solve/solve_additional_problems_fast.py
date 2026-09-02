#!/usr/bin/env python3
import argparse
import random
import re
import secrets
import socket
import sys
from math import prod

# Challenge constants
B = 2**126  # max size of N*r for the flag/oracle encryptions
# Use the largest primes first: 17 residues already give a CRT modulus > 2^128.
PRIMES_128_255 = [251, 241, 239, 233, 229, 227, 223, 211, 199, 197, 193, 191, 181, 179, 173, 167, 163, 157, 151, 149, 139, 137, 131]


def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)


def invmod(a, m):
    g, x, _ = egcd(a % m, m)
    if g != 1:
        raise ValueError("inverse does not exist")
    return x % m


def crt_pair(a, m, b, n):
    # m and n are coprime in this solver because we use primes.
    k = ((b - a) % n) * invmod(m, n) % n
    return (a + m * k) % (m * n), m * n


def is_probable_prime(n):
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
    # Deterministic enough for 128-bit challenge keys.
    for a in [2, 3, 5, 7, 11, 13, 17, 29, 31, 37, 41, 43, 47]:
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


def get_prime(bits):
    while True:
        n = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        # simple next-prime loop, enough for local self-test
        while n.bit_length() == bits:
            if is_probable_prime(n):
                return n
            n += 2


def dghv_encrypt_local(p, N, m):
    q = random.getrandbits(1024)
    # The released server used `/`, which is a float on modern Python.
    # This local copy uses the intended integer bound.
    rmax = 2**128 // N // 4
    r = random.randint(0, rmax)
    return p * q + N * r + m


def decrypt_flag(flag_cts, p):
    bs = bytes([(c % p) % 128 for c in flag_cts])
    return bs


class LocalOracle:
    def __init__(self, flag=b"crypto{local_test_flag}"):
        self.p = get_prime(128)
        self.flag = flag
        self.flag_cts = [dghv_encrypt_local(self.p, 128, ch) for ch in flag]
        self.queries = 0

    def trial_batch(self, N, t, count):
        # Vectorised local oracle. The p*q term disappears after c % p, so
        # we only simulate the noise. This keeps local testing fast while being
        # algebraically identical for the leak used by the attack.
        self.queries += 1
        rmax = 2**128 // N // 4
        out = []
        for _ in range(count):
            total_noise = 0
            for _ in range(t):
                total_noise += N * random.randint(0, rmax)
            out.append((total_noise % self.p) % N)
        return out

    def trial(self, N, t):
        return self.trial_batch(N, t, 1)[0]


class Tube:
    def __init__(self, host, port, timeout=10):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        self.buf = b""

    def recv_until(self, delim):
        while delim not in self.buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise EOFError("connection closed")
            self.buf += chunk
        idx = self.buf.index(delim) + len(delim)
        out = self.buf[:idx]
        self.buf = self.buf[idx:]
        return out

    def recv_line(self):
        return self.recv_until(b"\n")

    def sendline(self, data):
        if isinstance(data, str):
            data = data.encode()
        self.sock.sendall(data + b"\n")

    def close(self):
        self.sock.close()


class RemoteOracle:
    def __init__(self, host, port, timeout=10):
        self.tube = Tube(host, port, timeout)
        banner = self.tube.recv_until(b"Choose N: ")
        text = banner.decode(errors="replace")
        self.flag_cts = [int(x) for x in re.findall(r"^\s+(\d{50,})\s*$", text, flags=re.M)]
        if not self.flag_cts:
            raise RuntimeError("Could not parse encrypted flag from banner")
        self.at_choose_n = True
        self.queries = 0

    @staticmethod
    def _zero_hex(count):
        # Keep below server's recv(1024). No spaces, so count=400 => 800 bytes.
        return "00" * count

    def _start_new(self, N, count):
        if not self.at_choose_n:
            self.tube.recv_until(b"> ")
            self.tube.sendline("1")
            self.tube.recv_until(b"Choose N: ")
        self.tube.sendline(str(N))
        self.tube.recv_until(b"Message to encode")
        self.tube.recv_until(b": ")
        self.tube.sendline(self._zero_hex(count))
        self.at_choose_n = False

    def _add_zero(self, count):
        self.tube.recv_until(b"> ")
        self.tube.sendline("2")
        self.tube.recv_until(b"Message to encode")
        self.tube.recv_until(b": ")
        self.tube.sendline(self._zero_hex(count))

    def _decrypt_batch(self):
        self.tube.recv_until(b"> ")
        self.tube.sendline("3")
        self.tube.recv_until(b"Decrypted message: ")
        line = self.tube.recv_line().strip()
        if not line:
            return []
        return list(bytes.fromhex(line.decode().replace(" ", "")))

    def trial_batch(self, N, t, count):
        self.queries += 1
        self._start_new(N, count)
        for _ in range(t - 1):
            self._add_zero(count)
        return self._decrypt_batch()

    def trial(self, N, t):
        return self.trial_batch(N, t, 1)[0]

    def close(self):
        self.tube.close()


def _residue_from_samples(samples, N, t):
    nonzero = [y for y in samples if y != 0]
    if not nonzero:
        return None, 0, "no-wrap"

    vals = sorted(set(nonzero))
    if t == 4:
        # For t=4, noise < 2p, so every non-zero sample is exactly -p mod N.
        return (-vals[0]) % N, len(nonzero), "exact-t4"

    if len(vals) == 1:
        # Accepted only in the high-p region where k=1 is the only observed wrap.
        return (-vals[0]) % N, len(nonzero), f"consistent-t{t}"

    return None, len(nonzero), f"ambiguous-t{t}"


def recover_residue_mod_N(oracle, N, batch_size=400, extra_batches=2, verbose=False):
    """
    Batched version.  A single server request encrypts a vector of many zero
    bytes, then decrypts the vector, giving many independent samples at once.

    This changes the remote cost from dozens of menu/decrypt cycles per N to
    normally one cycle per N.
    """
    for t in (4, 5, 6, 7):
        for batch_no in range(extra_batches + 1):
            samples = oracle.trial_batch(N, t, batch_size)
            residue, hits, status = _residue_from_samples(samples, N, t)
            if verbose:
                print(f"[debug] N={N} t={t} batch={batch_no+1}: hits={hits}/{batch_size}, {status}")
            if residue is not None:
                return residue, t, hits
            # If t is ambiguous, a larger t is more likely to be safe for the
            # high-p case; do not waste extra batches at this t.
            if status.startswith("ambiguous"):
                break
    return None, None, 0


def recover_p(oracle, batch_size=400, extra_batches=2, verbose=True):
    x, m = 0, 1
    used = []
    for N in PRIMES_128_255:
        residue, t, hits = recover_residue_mod_N(oracle, N, batch_size=batch_size, extra_batches=extra_batches, verbose=False)
        if residue is None:
            if verbose:
                print(f"[-] N={N}: no residue recovered")
            continue
        x, m = crt_pair(x, m, residue, N)
        used.append((N, residue))
        if verbose:
            print(f"[+] p mod {N} = {residue:3d}; CRT={m.bit_length():3d} bits; t={t}; hits={hits}/{batch_size}")
        if m > 2**128:
            candidate = x
            if 2**127 <= candidate < 2**128:
                if verbose:
                    q = getattr(oracle, "queries", "?")
                    print(f"[+] recovered 128-bit candidate p using {len(used)} residues, oracle batches={q}")
                return candidate, used
            raise RuntimeError(f"CRT passed 2^128 but candidate has wrong size: {candidate}")
    raise RuntimeError("Not enough residues recovered; increase --batch-size or --extra-batches and retry")

def looks_like_flag(bs):
    try:
        s = bs.decode()
    except UnicodeDecodeError:
        return False
    printable = all(32 <= c < 127 for c in bs)
    return printable and (s.startswith("crypto{") or s.startswith("CSC{") or s.startswith("flag{"))


def solve_local(batch_size=400, extra_batches=2):
    oracle = LocalOracle()
    print(f"[local] real p      = {oracle.p}")
    print(f"[local] flag length = {len(oracle.flag_cts)}")
    p, _ = recover_p(oracle, batch_size=batch_size, extra_batches=extra_batches, verbose=True)
    flag = decrypt_flag(oracle.flag_cts, p)
    print(f"[local] recovered p = {p}")
    print(f"[local] decrypted   = {flag.decode(errors='replace')}")
    if p != oracle.p:
        raise SystemExit("local self-test failed: wrong p")
    if flag != oracle.flag:
        raise SystemExit("local self-test failed: wrong flag")
    print("[local] self-test OK")


def solve_remote(host, port, timeout, batch_size=400, extra_batches=2):
    oracle = RemoteOracle(host, port, timeout)
    print(f"[remote] parsed {len(oracle.flag_cts)} encrypted flag bytes")
    p, _ = recover_p(oracle, batch_size=batch_size, extra_batches=extra_batches, verbose=True)
    flag = decrypt_flag(oracle.flag_cts, p)
    print(f"[remote] recovered p = {p}")
    print(f"[remote] decrypted bytes = {flag!r}")
    try:
        print(f"[remote] flag = {flag.decode()}")
    except UnicodeDecodeError:
        pass
    if not looks_like_flag(flag):
        print("[!] Decryption does not look like a normal flag. Retry or increase trials_per_t.")
    oracle.close()


def main():
    ap = argparse.ArgumentParser(description="Fast batched solver for CryptoHack 'Additional problems (CSC Belgium)'")
    ap.add_argument("--local", action="store_true", help="run a local simulated self-test first")
    ap.add_argument("--remote", nargs=2, metavar=("HOST", "PORT"), help="solve a remote server")
    ap.add_argument("--timeout", type=int, default=10)
    ap.add_argument("--batch-size", type=int, default=400, help="zero bytes per batched oracle query; keep <= 500 for server recv(1024)")
    ap.add_argument("--extra-batches", type=int, default=2, help="additional batches to try per t if no wrap is observed")
    args = ap.parse_args()

    if not args.local and not args.remote:
        ap.print_help()
        return
    if args.local:
        solve_local(batch_size=args.batch_size, extra_batches=args.extra_batches)
    if args.remote:
        host, port_s = args.remote
        solve_remote(host, int(port_s), args.timeout, batch_size=args.batch_size, extra_batches=args.extra_batches)


if __name__ == "__main__":
    main()
