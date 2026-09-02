#!/usr/bin/env python3
import argparse
import hashlib
import itertools
import math
import os
import random
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

B_DEFAULT = 10**9
MAX_INDEX_DEFAULT = 10_000_000

# ---------- small integer factoring for n mod q = (B+i)(B+j) (< 2^64 with defaults) ----------

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
    # deterministic for <2^64; probabilistic beyond, good enough for local simulator
    if n < (1 << 64):
        bases = [2, 3, 5, 7, 11, 13, 17]
    else:
        bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for a in bases:
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


def pollard_rho(n: int) -> int:
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    while True:
        c = random.randrange(1, n - 1)
        x = random.randrange(0, n - 1)
        y = x
        d = 1
        while d == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = math.gcd(abs(x - y), n)
        if d != n:
            return d


def factorint(n: int) -> dict[int, int]:
    out: dict[int, int] = {}
    def rec(m: int) -> None:
        if m == 1:
            return
        if is_probable_prime(m):
            out[m] = out.get(m, 0) + 1
            return
        d = pollard_rho(m)
        rec(d)
        rec(m // d)
    rec(n)
    return out


def divisors_from_factorization(fac: dict[int, int]) -> list[int]:
    divs = [1]
    for p, e in fac.items():
        cur = []
        pe = 1
        for _ in range(e + 1):
            for d in divs:
                cur.append(d * pe)
            pe *= p
        divs = cur
    return divs

# ---------- polynomial arithmetic over GF(q), dense low-to-high ----------

def div_round(num: int, den: int) -> int:
    assert den > 0
    if num >= 0:
        return (num + den // 2) // den
    return -((-num + den // 2) // den)


def trim(poly: list[int], mod: int) -> list[int]:
    while poly and poly[-1] % mod == 0:
        poly.pop()
    return poly


def remove_x_factors(poly: list[int], mod: int) -> list[int]:
    i = 0
    while i < len(poly) and poly[i] % mod == 0:
        i += 1
    return poly[i:]


def div_linear(poly: list[int], root: int, mod: int) -> list[int]:
    # Divide by x-root; low-to-high coefficients.
    poly = trim([c % mod for c in poly], mod)
    n = len(poly) - 1
    if n <= 0:
        return []
    qpoly = [0] * n
    qpoly[-1] = poly[-1]
    for k in range(n - 2, -1, -1):
        qpoly[k] = (poly[k + 1] + root * qpoly[k + 1]) % mod
    rem = (poly[0] + root * qpoly[0]) % mod
    if rem != 0:
        raise ValueError("polynomial was not divisible by expected linear factor")
    return trim(qpoly, mod)


def poly_mod(a: list[int], b: list[int], mod: int) -> list[int]:
    a = trim([x % mod for x in a], mod)
    b = trim([x % mod for x in b], mod)
    if not b:
        raise ZeroDivisionError
    inv_lc = pow(b[-1], -1, mod)
    db = len(b) - 1
    while len(a) >= len(b) and a:
        coef = (a[-1] * inv_lc) % mod
        if coef:
            off = len(a) - len(b)
            # b is usually dense after the first Euclidean step.
            for i in range(db + 1):
                a[off + i] = (a[off + i] - coef * b[i]) % mod
        while a and a[-1] == 0:
            a.pop()
    return a


def poly_gcd(a: list[int], b: list[int], mod: int) -> list[int]:
    a = trim([x % mod for x in a], mod)
    b = trim([x % mod for x in b], mod)
    while b:
        if len(a) < len(b):
            a, b = b, a
        a, b = b, poly_mod(a, b, mod)
    if not a:
        return []
    inv = pow(a[-1], -1, mod)
    return [(c * inv) % mod for c in a]

# ---------- exploit math ----------

def candidate_pairs_from_modulus(N: int, q: int, B: int, max_index: int) -> list[tuple[int, int, int, int]]:
    R = N % q
    fac = factorint(R)
    pairs = set()
    for d in divisors_from_factorization(fac):
        if d == 0 or R % d:
            continue
        e = R // d
        if B <= d < B + max_index and B <= e < B + max_index:
            i, j = d - B, e - B
            if i <= j:
                pairs.add((i, j, d, e))
            else:
                pairs.add((j, i, e, d))
    return sorted(pairs)


def determinant_poly(rows: tuple[int, int, int], pairs: list[tuple[int, int, int, int]], cvals: list[int], q: int) -> list[int]:
    r0, r1, r2 = rows
    S = [((p[2] + p[3]) % q) for p in pairs]
    C = [c % q for c in cvals]
    coeffs = {
        r0: (S[r1] * C[r2] - C[r1] * S[r2]) % q,
        r1: (-S[r0] * C[r2] + C[r0] * S[r2]) % q,
        r2: (S[r0] * C[r1] - C[r0] * S[r1]) % q,
    }
    sparse: dict[int, int] = {}
    for row, scale in coeffs.items():
        i, j, xi, xj = pairs[row]
        sparse[j] = (sparse.get(j, 0) + scale * xi) % q
        sparse[i] = (sparse.get(i, 0) + scale * xj) % q
    if not sparse:
        return []
    deg = max(sparse)
    poly = [0] * (deg + 1)
    for exp, coef in sparse.items():
        poly[exp] = coef % q
    poly = remove_x_factors(trim(poly, q), q)
    # r=1 is a structural root because a_row(1)=x_i+x_j=S_row.
    poly = div_linear(poly, 1, q)
    return poly


def recover_second_lcg_multiplier(pairs: list[tuple[int, int, int, int]], cvals: list[int], q: int) -> int:
    polys = []
    for rows in itertools.combinations(range(4), 3):
        p = determinant_poly(rows, pairs, cvals, q)
        if len(p) > 1:
            polys.append(p)
    if len(polys) < 2:
        raise ValueError("not enough non-trivial determinant polynomials")
    g = polys[0]
    for p in polys[1:]:
        g = poly_gcd(g, p, q)
    if len(g) != 2:
        raise ValueError(f"unexpected gcd degree {len(g)-1}; try a new connection")
    return (-g[0] * pow(g[1], -1, q)) % q


def recover_second_lcg_values(a: int, pairs: list[tuple[int, int, int, int]], cvals: list[int], q: int) -> dict[int, int]:
    Arows = []
    Srows = []
    for i, j, xi, xj in pairs:
        Arows.append((xi * pow(a, j, q) + xj * pow(a, i, q)) % q)
        Srows.append((xi + xj) % q)
    u = v = None
    for r in range(4):
        for s in range(r + 1, 4):
            den = (Arows[r] * Srows[s] - Arows[s] * Srows[r]) % q
            if den:
                inv = pow(den, -1, q)
                u = ((cvals[r] * Srows[s] - cvals[s] * Srows[r]) * inv) % q
                v = ((Arows[r] * cvals[s] - Arows[s] * cvals[r]) * inv) % q
                break
        if u is not None:
            break
    if u is None:
        raise ValueError("could not solve for affine form of second LCG")
    ys = {}
    for i, j, _, _ in pairs:
        ys[i] = (u * pow(a, i, q) + v) % q
        ys[j] = (u * pow(a, j, q) + v) % q
    return ys

# Solve A*z + B*w == h (mod Q) with 0 <= z,w < q using a 2D closest-vector search.

def gauss_reduce(b1: tuple[int, int], b2: tuple[int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
    b1 = [int(b1[0]), int(b1[1])]
    b2 = [int(b2[0]), int(b2[1])]
    def dot(u, v): return u[0] * v[0] + u[1] * v[1]
    def norm2(u): return dot(u, u)
    while True:
        if norm2(b2) < norm2(b1):
            b1, b2 = b2, b1
            continue
        mu = div_round(dot(b1, b2), norm2(b1))
        if mu == 0:
            return (b1[0], b1[1]), (b2[0], b2[1])
        b2[0] -= mu * b1[0]
        b2[1] -= mu * b1[1]


def small_modular_line_solutions(q: int, alpha: int, beta: int, radius_mult: int = 3) -> list[tuple[int, int]]:
    Q = q * q
    b1, b2 = gauss_reduce((-Q, 0), (alpha, 1))
    target = (-beta, 0)
    def dot(u, v): return u[0] * v[0] + u[1] * v[1]
    n1 = dot(b1, b1)
    ip21 = dot(b2, b1)
    det = b1[0] * b2[1] - b1[1] * b2[0]
    num_c = dot(target, b2) * n1 - dot(target, b1) * ip21
    den_c = det * det
    center = div_round(num_c, den_c)
    # Conservative exact-width enumeration around the closest projected coefficient.
    width = radius_mult * (math.isqrt(n1) // q + 2) + 16
    out = []
    for c2 in range(center - width, center + width + 1):
        t1 = (target[0] - c2 * b2[0], target[1] - c2 * b2[1])
        c1 = div_round(dot(t1, b1), n1)
        for cc1 in range(c1 - 24, c1 + 25):
            vx = cc1 * b1[0] + c2 * b2[0]
            vy = cc1 * b1[1] + c2 * b2[1]
            z = vy
            w = vx + beta
            if 0 <= z < q and 0 <= w < q:
                out.append((z, w))
    return list(dict.fromkeys(out))


def factor_with_two_base_q_digits(N: int, q: int, r1: int, r2: int) -> tuple[int, int]:
    Q = q * q
    H = (N - r1 * r2) // Q
    h = H % Q
    alpha = (-r2 * pow(r1, -1, Q)) % Q
    beta = (h * pow(r1, -1, Q)) % Q
    for z, w in small_modular_line_solutions(q, alpha, beta):
        p = r1 + Q * z
        r = r2 + Q * w
        if p * r == N:
            return p, r
    raise ValueError("CVP step did not recover a factorization")


def attack_from_values(q: int, moduli: list[int], B: int = B_DEFAULT, max_index: int = MAX_INDEX_DEFAULT, verbose: bool = True) -> list[tuple[int, int]]:
    all_pair_options = []
    for n in moduli:
        opts = candidate_pairs_from_modulus(n, q, B, max_index)
        if verbose:
            print(f"[+] candidate index pairs from n mod q: {opts}", flush=True)
        if not opts:
            raise ValueError("no index pair found; increase max_index or retry")
        all_pair_options.append(opts)

    cvals = [(n // q) % q for n in moduli]
    for chosen_pairs in itertools.product(*all_pair_options):
        pairs = list(chosen_pairs)
        try:
            a2 = recover_second_lcg_multiplier(pairs, cvals, q)
            if a2 in (0, 1):
                continue
            ys = recover_second_lcg_values(a2, pairs, cvals, q)
            factors = []
            for n, (i, j, xi, xj) in zip(moduli, pairs):
                r1 = xi + q * ys[i]
                r2 = xj + q * ys[j]
                p, r = factor_with_two_base_q_digits(n, q, r1, r2)
                factors.append((p, r))
            if all(p * r == n for (p, r), n in zip(factors, moduli)):
                if verbose:
                    print(f"[+] recovered second LCG multiplier a = {a2}", flush=True)
                return factors
        except Exception as exc:
            if verbose:
                print(f"[-] pair choice failed: {exc}", flush=True)
            continue
    raise ValueError("all pair choices failed")

# ---------- local simulator ----------

def random_prime(bits: int) -> int:
    while True:
        n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(n):
            return n


def local_test(qbits: int = 80, B: int = 10**6) -> None:
    print(f"[*] local simulator with qbits={qbits}, B={B}", flush=True)
    q = random_prime(qbits)
    a2, x2, b2 = random.randrange(1, q), random.randrange(1, q), random.randrange(1, q)
    a3, x3, b3 = random.randrange(1, q), random.randrange(1, q), random.randrange(1, q)
    y, z = x2, x3
    primes = []
    indices = []
    idx = 0
    while len(primes) < 8:
        x = B + idx
        p = z * q * q + y * q + x
        if is_probable_prime(p):
            primes.append(p)
            indices.append(idx)
        y = (a2 * y + b2) % q
        z = (a3 * z + b3) % q
        idx += 1
    moduli = [primes[i] * primes[i + 1] for i in range(0, 8, 2)]
    print(f"[+] true accepted indices: {indices}", flush=True)
    factors = attack_from_values(q, moduli, B=B, max_index=1_000_000, verbose=True)
    assert all(factors[i][0] * factors[i][1] == moduli[i] for i in range(4))
    print("[+] local factorization succeeded")
    print("[+] first local factor bit lengths:", factors[0][0].bit_length(), factors[0][1].bit_length())

# ---------- remote IO and PoW ----------

class Tube:
    def __init__(self, host: str, port: int, timeout: float = 300.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        self.buf = b""
    def recvline(self) -> bytes:
        while b"\n" not in self.buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise EOFError("connection closed")
            self.buf += chunk
        line, self.buf = self.buf.split(b"\n", 1)
        return line + b"\n"
    def sendline(self, s: str | int) -> None:
        if isinstance(s, int):
            s = str(s)
        self.sock.sendall(s.encode() + b"\n")
    def close(self) -> None:
        self.sock.close()


def compile_pow_solver() -> Path | None:
    src = r'''
#include <openssl/sha.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdatomic.h>
#ifdef _OPENMP
#include <omp.h>
#endif
static int append_u64(char *buf, uint64_t x){
    char tmp[32]; int n=0;
    if(x==0){ buf[0]='0'; return 1; }
    while(x){ tmp[n++] = '0' + (x % 10); x /= 10; }
    for(int i=0;i<n;i++) buf[i]=tmp[n-1-i];
    return n;
}
int main(int argc, char **argv){
    if(argc < 2) return 2;
    const char *prefix = argv[1];
    int plen = (int)strlen(prefix);
    atomic_int done = 0;
    atomic_ullong answer = 0;
    #pragma omp parallel
    {
        int tid = 0, nth = 1;
        #ifdef _OPENMP
        tid = omp_get_thread_num(); nth = omp_get_num_threads();
        #endif
        char msg[128]; unsigned char md[SHA256_DIGEST_LENGTH];
        memcpy(msg, prefix, plen);
        for(uint64_t i=(uint64_t)tid; !atomic_load(&done); i += (uint64_t)nth){
            int n = append_u64(msg + plen, i);
            SHA256((unsigned char*)msg, plen + n, md);
            if((md[28] & 3) == 0 && md[29] == 0 && md[30] == 0 && md[31] == 0){
                answer = i; atomic_store(&done, 1); break;
            }
        }
    }
    printf("%llu\n", (unsigned long long)answer);
    return 0;
}
'''
    tmp = Path(tempfile.gettempdir()) / "cryptohack_pow_solver.c"
    exe = Path(tempfile.gettempdir()) / "cryptohack_pow_solver"
    try:
        tmp.write_text(src)
        subprocess.check_call(["gcc", "-O3", "-fopenmp", str(tmp), "-lcrypto", "-o", str(exe)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return exe
    except Exception:
        return None


def solve_pow(prefix: str) -> str:
    exe = compile_pow_solver()
    if exe is not None:
        return subprocess.check_output([str(exe), prefix], text=True).strip()
    # Slow fallback; acceptable under the challenge's long alarm on a decent machine.
    pref = prefix.encode()
    i = 0
    while True:
        ans = str(i).encode()
        d = hashlib.sha256(pref + ans).digest()
        if (d[28] & 3) == 0 and d[29] == 0 and d[30] == 0 and d[31] == 0:
            return str(i)
        i += 1


def recv_until_q(t: Tube) -> int:
    while True:
        line = t.recvline().decode(errors="replace").strip()
        print(line, flush=True)
        if line.startswith("q = "):
            return int(line.split("=", 1)[1].strip())


def recv_next_int(t: Tube) -> int:
    while True:
        line = t.recvline().decode(errors="replace").strip()
        print(line, flush=True)
        try:
            return int(line)
        except ValueError:
            continue


def remote_attack(host: str, port: int, B: int, max_index: int) -> None:
    t = Tube(host, port)
    try:
        line = t.recvline().decode().strip()
        print(line, flush=True)
        if "PoW" in line:
            prefix = t.recvline().decode().strip()
            print(prefix, flush=True)
            ans = solve_pow(prefix)
            print(f"[+] PoW answer: {ans}", flush=True)
            t.sendline(ans)
        else:
            raise RuntimeError("unexpected initial banner")
        q = recv_until_q(t)
        print(f"[+] q bits: {q.bit_length()}", flush=True)
        # Choose LCG1: x_k = B+k, no wrap for all realistic accepted indices.
        t.sendline(1)
        t.sendline(B)
        t.sendline(1)
        moduli = [recv_next_int(t) for _ in range(4)]
        factors = attack_from_values(q, moduli, B=B, max_index=max_index, verbose=True)
        for p, r in factors:
            t.sendline(p)
            t.sendline(r)
        # The flag is the next printed line.
        while True:
            try:
                print(t.recvline().decode(errors="replace").rstrip(), flush=True)
            except EOFError:
                break
    finally:
        t.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="Solve CryptoHack RSA Secret Sharing (WACON)")
    ap.add_argument("--local", action="store_true", help="run local simulator test first")
    ap.add_argument("--remote", action="store_true", help="attack the CryptoHack archive server")
    ap.add_argument("--host", default="archive.cryptohack.org")
    ap.add_argument("--port", type=int, default=42957)
    ap.add_argument("--B", type=int, default=B_DEFAULT)
    ap.add_argument("--max-index", type=int, default=MAX_INDEX_DEFAULT)
    ap.add_argument("--qbits", type=int, default=80, help="local simulator q bit size")
    args = ap.parse_args()
    if args.local:
        # Use a smaller B in the local simulator if qbits is small.
        local_B = 10**6 if args.qbits < 128 else args.B
        local_test(args.qbits, local_B)
    if args.remote:
        remote_attack(args.host, args.port, args.B, args.max_index)
    if not args.local and not args.remote:
        ap.print_help()

if __name__ == "__main__":
    main()
