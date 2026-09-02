#!/usr/bin/env python3
import ast
import math
import re
import time
from multiprocessing import Pool, cpu_count
from pathlib import Path

# ECSC 2023 Norway - Hide and seek
# Usage: python3 solve_hide_and_seek.py /path/to/output.txt

p = 1789850433742566803999659961102071018708588095996784752439608585988988036381340404632423562593
A = 62150203092456938230366891668382702110196631396589305390157506915312399058961554609342345998
B = 1005820216843804918712728918305396768000492821656453232969553225956348680715987662653812284211

# #E(F_p), computed once with Sage/PARI: EllipticCurve(GF(p), [A,B]).order()
N = 1789850433742566803999659961102071018708588095980691155136886508769519951605603261424289500493
FACTORS = [
    12775224751, 13026062843, 18511195699,
    24508446437, 25961704469, 28450356619,
    31034521019, 31982226581, 32337773063,
]
O = None  # point at infinity; ordinary points are (x, y)


def inv(x):
    return pow(x % p, -1, p)


def neg(P):
    if P is None:
        return None
    return (P[0], (-P[1]) % p)


def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + A) * inv(2 * y1) % p
    else:
        lam = (y2 - y1) * inv(x2 - x1) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def mul(k, P):
    if k == 0 or P is None:
        return None
    if k < 0:
        return mul(-k, neg(P))
    R = None
    Q = P
    while k:
        if k & 1:
            R = add(R, Q)
        Q = add(Q, Q)
        k >>= 1
    return R


def parse_output(path):
    s = Path(path).read_text()
    s = re.sub(r'\((\d+)\s*:\s*(\d+)\s*:\s*1\)', r'(\1, \2)', s)
    arr = ast.literal_eval(s)
    rows, pts = [], []
    for a, b, (x, y) in arr:
        rows.append((int(a), int(b)))
        pts.append((int(x), int(y)))
    return rows, pts


def egcd(a, b):
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    if old_r < 0:
        old_r, old_s, old_t = -old_r, -old_s, -old_t
    return old_r, old_s, old_t


def recover_P_Q(rows, pts):
    """Use integer Bezout on 2x2 minors of coefficient rows.

    R_i = a_i P + b_i Q.  For two rows i,j with determinant d:
      b_j R_i - b_i R_j = d P
     -a_j R_i + a_i R_j = d Q
    If gcd of determinants is 1, combine these equations to get P and Q.
    """
    pairs, dets = [], []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            ai, bi = rows[i]
            aj, bj = rows[j]
            d = ai * bj - aj * bi
            if d:
                pairs.append((i, j))
                dets.append(d)

    coefs = [0] * len(dets)
    g = 0
    used = -1
    for idx, d in enumerate(dets):
        if g == 0:
            g = abs(d)
            coefs[idx] = 1 if d > 0 else -1
        else:
            ng, x, y = egcd(g, d)
            for t in range(len(coefs)):
                coefs[t] *= x
            coefs[idx] += y
            g = ng
        used = idx
        if g == 1:
            break
    assert g == 1

    cP = [0] * len(rows)
    cQ = [0] * len(rows)
    for t in range(used + 1):
        u = coefs[t]
        if not u:
            continue
        i, j = pairs[t]
        ai, bi = rows[i]
        aj, bj = rows[j]
        cP[i] += u * bj
        cP[j] -= u * bi
        cQ[i] -= u * aj
        cQ[j] += u * ai

    P = None
    Q = None
    for c, R in zip(cP, pts):
        if c:
            P = add(P, mul(c, R))
    for c, R in zip(cQ, pts):
        if c:
            Q = add(Q, mul(c, R))
    return P, Q


def bsgs_prime_order(G, H, q):
    m = math.isqrt(q) + 1
    table = {}
    R = None
    for j in range(m):
        table.setdefault(R, j)
        R = add(R, G)
    step = neg(mul(m, G))
    gamma = H
    for i in range(m + 1):
        j = table.get(gamma)
        if j is not None:
            x = i * m + j
            if x < q:
                return x
        gamma = add(gamma, step)
    raise RuntimeError(f'dlog not found modulo {q}')


def solve_mod_q(args):
    P, Q, q = args
    h = N // q
    Gq = mul(h, P)
    Hq = mul(h, Q)
    t = time.time()
    xq = bsgs_prime_order(Gq, Hq, q)
    return q, xq, time.time() - t


def crt_pair(a1, m1, a2, m2):
    # m1, m2 are coprime
    t = ((a2 - a1) * pow(m1, -1, m2)) % m2
    return (a1 + m1 * t) % (m1 * m2), m1 * m2


def crt_all(moduli, residues):
    x, m = residues[0], moduli[0]
    for ai, mi in zip(residues[1:], moduli[1:]):
        x, m = crt_pair(x, m, ai, mi)
    return x


def main():
    import sys
    if len(sys.argv) > 1:
        out_path = Path(sys.argv[1])
    else:
        out_path = Path('output_5058c28a109d275ad4f16a27a5330d28.txt')

    rows, pts = parse_output(out_path)
    print(f'[+] parsed {len(rows)} hidden points')
    P, Q = recover_P_Q(rows, pts)
    print('[+] recovered P and Q')

    # local sanity check
    for i in range(3):
        a, b = rows[i]
        assert add(mul(a, P), mul(b, Q)) == pts[i]
    assert mul(N, P) is None
    print('[+] local checks passed')

    workers = min(4, cpu_count(), len(FACTORS))
    with Pool(processes=workers) as pool:
        parts = pool.map(solve_mod_q, [(P, Q, q) for q in FACTORS])

    parts.sort(key=lambda t: FACTORS.index(t[0]))
    residues = []
    for q, xq, sec in parts:
        print(f'[+] flag mod {q} = {xq}  ({sec:.2f}s)')
        residues.append(xq)

    flag_int = crt_all(FACTORS, residues)
    inner = flag_int.to_bytes((flag_int.bit_length() + 7) // 8, 'big')
    print('[+] flag:', 'ECSC{' + inner.decode() + '}')


if __name__ == '__main__':
    main()
