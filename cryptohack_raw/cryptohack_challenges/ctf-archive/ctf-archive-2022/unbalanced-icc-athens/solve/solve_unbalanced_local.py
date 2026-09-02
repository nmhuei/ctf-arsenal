#!/usr/bin/env python3
from math import gcd
import sympy as sp
from sympy import symbols, Poly
from fpylll import IntegerMatrix, LLL

N = int('7506dad690d57202571d4138e6743e22834072087ef1f81f227409dda108854f2f10c23150dcfbe79940effde0603f64f77f8c123f6ad27ee0ebb3665de8cdb46ced5d2c69f4d9170d406fd93466f8400001b20ea8d084bbb06b28b0ca3782ca2bd92ac012d08103e3477f8ff83c836ebbda570a803bb5b0611b9b285188da53', 16)
e = int('480fe3b95d6ebadae2a222b6161b8aa0cbb61e0571da3658dac4cf174c7670514c70d8b337408bac467d6a39804efb35394f6d83941fa2d25ca542f630db5b54efaf347062fb828cb7473728de0510f3b27b906c9dd056f77d1ceb0fb249fcc5fe4ee219be82cdb6cee2578b8fa8ad7b489ee45edff4349c4a03af42cc232f65', 16)
c = int('24581cf0e782e1d6b9d6337e26d87ba16fbf8e5887b83522738769ffa59b38f76eafa61fe9a373948677101f5abe2a4e4032b11ff1c903fe9a0368d07212706bdb4cf24532df6819570ef6935fd3aa5e25f4f65c35a1d6362c8dc3eef95ec15ede94d2acf5ce15cfb81c37bcda4a83660006898f07bf40b072d9382a63b5ab4b', 16)

x, y, z = symbols('x y z')


def reduce_yz(expr):
    """Reduce monomials with the relation y*z = N."""
    P = Poly(expr, x, y, z, domain='ZZ')
    out = 0
    for (dx, dy, dz), coeff in P.terms():
        r = min(dy, dz)
        out += int(coeff) * (N ** r) * x ** dx * y ** (dy - r) * z ** (dz - r)
    return Poly(out, x, y, z, domain='ZZ')


def build_lattice(m=5, t=5, a=0):
    # Root is x = 2*k, y = p, z = q.
    # Since e*d - 1 = k*phi, we have 2 + 2*k*phi == 0 (mod e).
    f = Poly(2 + x * (N + 1 - y - z), x, y, z, domain='ZZ')
    polys = []

    for kk in range(m):
        fk = f ** kk
        for i in range(1, m - kk + 1):
            for b in range(2):
                polys.append(reduce_yz((e ** (m - kk)) * x ** i * y ** a * z ** b * fk.as_expr()))

    for kk in range(m + 1):
        fk = f ** kk
        for j in range(t + 1):
            polys.append(reduce_yz((e ** (m - kk)) * y ** (a + j) * fk.as_expr()))

    monoms = sorted(
        {mon for P in polys for mon in P.monoms()},
        key=lambda abc: (abc[0] + abc[1] + abc[2], abc[0], abc[1], abc[2]),
    )
    bounds = (2 ** 300, 2 ** 256, 2 ** 768)
    X, Y, Z = bounds

    M = IntegerMatrix(len(polys), len(monoms))
    for r, P in enumerate(polys):
        D = P.as_dict()
        for col, mon in enumerate(monoms):
            M[r, col] = int(D.get(mon, 0)) * X ** mon[0] * Y ** mon[1] * Z ** mon[2]

    LLL.reduction(M, delta=0.99, eta=0.501)

    H = []
    for r in range(M.nrows):
        expr = 0
        for col, mon in enumerate(monoms):
            scale = X ** mon[0] * Y ** mon[1] * Z ** mon[2]
            coeff = int(M[r, col])
            if coeff % scale:
                raise ValueError('non-integral coefficient after unscaling')
            coeff //= scale
            if coeff:
                expr += coeff * x ** mon[0] * y ** mon[1] * z ** mon[2]
        if expr:
            P = Poly(expr, x, y, z, domain='ZZ')
            if len(P.terms()) > 1:
                H.append([(dx, dy, dz, int(coeff)) for (dx, dy, dz), coeff in P.terms()])
    return H


def trim(poly):
    while poly and poly[-1] == 0:
        poly.pop()
    return poly


def poly_divmod(a, b, p):
    a = trim([v % p for v in a])
    b = trim([v % p for v in b])
    inv_lc = pow(b[-1], -1, p)
    q = [0] * max(1, len(a) - len(b) + 1)
    while len(a) >= len(b) and b:
        d = len(a) - len(b)
        coeff = a[-1] * inv_lc % p
        q[d] = coeff
        if coeff:
            for i in range(len(b)):
                a[d + i] = (a[d + i] - coeff * b[i]) % p
        trim(a)
    return trim(q), trim(a)


def poly_gcd(a, b, p):
    a = trim([v % p for v in a])
    b = trim([v % p for v in b])
    if not a:
        return b
    if not b:
        return a
    while b:
        _, r = poly_divmod(a, b, p)
        a, b = b, r
    inv = pow(a[-1], -1, p)
    return [(v * inv) % p for v in a]


def crt_pair(R, M, r, m):
    t = ((r - R) % m) * pow(M, -1, m) % m
    return (R + M * t) % (M * m), M * m


def recover_p(H):
    maxdx = max(dx for terms in H for dx, _, _, _ in terms)
    maxdy = max(dy for terms in H for _, dy, _, _ in terms)
    maxdz = max(dz for terms in H for _, _, dz, _ in terms)

    def coeffs_in_x(terms, yy, zz, mod, ypows, zpows):
        coeff = [0] * (maxdx + 1)
        for dx, dy, dz, c0 in terms:
            coeff[dx] = (coeff[dx] + (c0 % mod) * ypows[dy] * zpows[dz]) % mod
        return trim(coeff)

    def candidates_mod(mod, nH=4):
        if N % mod == 0:
            return []
        Nm = N % mod
        candidates = []
        for yy in range(1, mod):
            zz = Nm * pow(yy, -1, mod) % mod
            ypows = [1] * (maxdy + 1)
            zpows = [1] * (maxdz + 1)
            for i in range(1, maxdy + 1):
                ypows[i] = ypows[i - 1] * yy % mod
            for i in range(1, maxdz + 1):
                zpows[i] = zpows[i - 1] * zz % mod

            G = None
            ok = True
            for terms in H[:nH]:
                P = coeffs_in_x(terms, yy, zz, mod, ypows, zpows)
                if not P:
                    continue
                G = P if G is None else poly_gcd(G, P, mod)
                if len(G) == 1:
                    ok = False
                    break
            if ok and G and len(G) > 1:
                roots = []
                for xx in range(mod):
                    val = 0
                    for coeff in reversed(G):
                        val = (val * xx + coeff) % mod
                    if val == 0:
                        roots.append(xx)
                if roots:
                    candidates.append((yy, roots))
        return candidates

    R, M = 0, 1
    for prime in sp.primerange(1009, 10000):
        candidates = candidates_mod(prime)
        if len(candidates) != 1:
            continue
        R, M = crt_pair(R, M, candidates[0][0], prime)
        if M.bit_length() > 260:
            for pp in {R % M, (R % M) - M}:
                if pp > 1 and N % pp == 0:
                    return pp
    raise RuntimeError('p not recovered')


def main():
    H = build_lattice()
    p = recover_p(H)
    q = N // p
    assert p * q == N
    d = pow(e, -1, (p - 1) * (q - 1))
    m = pow(c, d, N)
    flag = m.to_bytes((m.bit_length() + 7) // 8, 'big')
    print(flag.decode())


if __name__ == '__main__':
    main()
