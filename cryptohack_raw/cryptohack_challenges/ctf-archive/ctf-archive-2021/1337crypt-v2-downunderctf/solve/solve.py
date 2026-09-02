#!/usr/bin/env python3
import ast
import math
import re
import sys
from fractions import Fraction
from pathlib import Path
from sympy import Matrix


def parse_output(path):
    s = Path(path).read_text()

    hint1 = int(re.search(r"hint1 = (\d+)", s).group(1))
    hint2 = ast.literal_eval(re.search(r"hint2 = (\[.*?\])\s*c =", s, re.S).group(1))

    # output Sage format: c = imag*I + real
    m = re.search(r"c = (\d+)\*I \+ (\d+)", s)
    ci, cr = int(m.group(1)), int(m.group(2))

    return hint1, hint2, (cr, ci)


def round_fraction(x):
    q, r = divmod(x.numerator, x.denominator)
    if 2 * r >= x.denominator:
        q += 1
    return q


def babai_closest_vector(row_basis, target):
    B = Matrix(row_basis).lll(delta=0.99)
    basis = [list(map(int, B.row(i))) for i in range(B.rows)]

    m = len(basis)
    n = len(target)

    # Exact Gram-Schmidt over rationals
    bstar = []
    bnorm = []

    for i, b in enumerate(basis):
        v = [Fraction(x) for x in b]

        for j in range(i):
            mu = sum(Fraction(b[k]) * bstar[j][k] for k in range(n)) / bnorm[j]
            v = [v[k] - mu * bstar[j][k] for k in range(n)]

        bstar.append(v)
        bnorm.append(sum(x * x for x in v))

    y = [Fraction(x) for x in target]
    cv = [0] * n

    for i in reversed(range(m)):
        coeff = round_fraction(
            sum(y[k] * bstar[i][k] for k in range(n)) / bnorm[i]
        )

        y = [y[k] - coeff * Fraction(basis[i][k]) for k in range(n)]
        cv = [cv[k] + coeff * basis[i][k] for k in range(n)]

    return cv


def recover_primes(hint1, hint2):
    D = 1 << 338

    E = []
    A = []
    B = []

    for H, a, b in hint2:
        E.append(D * D * (H - a * a - b * b * hint1))
        A.append(2 * a * b * D * D)
        B.append(2 * hint1 * b * D)

    # Linear approximation:
    #
    # E_i = A_i * p + B_i * v_i + small_i
    #
    # Unknowns: p, v1, v2
    # where v_i is the hidden 338-bit mantissa part.
    PBOUND = 1 << 1337
    VBOUND = D

    for cbit in range(3300, 3380):
        C = 1 << cbit

        sp = max(1, C // PBOUND)
        sv = max(1, C // VBOUND)

        rows = [
            [A[0], A[1], sp, 0, 0],
            [B[0], 0, 0, sv, 0],
            [0, B[1], 0, 0, sv],
        ]

        target = [E[0], E[1], 0, 0, 0]

        cv = babai_closest_vector(rows, target)

        if cv[2] % sp or cv[3] % sv or cv[4] % sv:
            continue

        p0 = cv[2] // sp

        # Babai gives p very close.
        # Small correction handles ignored lower-order terms.
        for delta in range(-2000, 2001):
            p = p0 + delta
            if p <= 0:
                continue

            q2 = hint1 - p * p
            if q2 <= 0:
                continue

            q = math.isqrt(q2)
            if q * q == q2:
                return p, q

    raise RuntimeError("failed to recover p, q")


def egcd(a, b):
    if b == 0:
        return a, 1, 0

    g, x, y = egcd(b, a % b)
    return g, y, x - (a // b) * y


def invmod(a, m):
    g, x, _ = egcd(a, m)
    assert g == 1
    return x % m


def gp_mul(x, y, n):
    a, b = x
    c, d = y

    return (
        (a * c - b * d) % n,
        (a * d + b * c) % n,
    )


def gp_pow(x, e, n):
    r = (1, 0)

    while e:
        if e & 1:
            r = gp_mul(r, x, n)

        x = gp_mul(x, x, n)
        e >>= 1

    return r


def long_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, "big")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} output.txt")
        sys.exit(1)

    hint1, hint2, c = parse_output(sys.argv[1])

    p, q = recover_primes(hint1, hint2)
    n = p * q

    e = 0x1337

    # In this output p % 4 == q % 4 == 1,
    # so Z_p[i], Z_q[i] split and exponent cycle divides lcm(p-1, q-1).
    lam = math.lcm(p - 1, q - 1)
    d = invmod(e, lam)

    _, flag_int = gp_pow(c, d, n)

    print(long_to_bytes(flag_int).decode())


if __name__ == "__main__":
    main()
