#!/usr/bin/env python3
from sage.all import *
from Crypto.Util.number import long_to_bytes
import itertools

def solve():
    with open("../challenge/crypto_from-nothing/output.txt") as f:
        text = f.read()
    ns = {}
    exec(text, ns)
    p = ns["p"]
    D_u_list = ns["D_u"]
    u_list = ns["u"]
    v_list = ns["v"]

    F = GF(p)
    R = PolynomialRing(F, "x")
    x = R.gen()

    H = HyperellipticCurve(x**11, 1, "u,v")
    J = H.jacobian()(F)
    ct = J(R(u_list), R(v_list))

    D_u = R(D_u_list)
    factors = [f for f, mult in D_u.factor()]

    roots_per_factor = []
    for fi in factors:
        deg = fi.degree()
        if deg == 1:
            xi = -fi[0]
            val = 1 + 4 * (xi**11)
            r = val.sqrt()
            v1 = (r - 1) / 2
            v2 = (-r - 1) / 2
            roots_per_factor.append([R(v1), R(v2)])
        else:
            K_ext = F.extension(fi, "a")
            a = K_ext.gen()
            val = 1 + 4 * (a**11)
            r = val.sqrt()
            v1_a = (r - 1) / 2
            v2_a = (-r - 1) / 2
            v1 = R(v1_a.polynomial())
            v2 = R(v2_a.polynomial())
            roots_per_factor.append([v1, v2])

    e_candidates = []
    for combo in itertools.product(*roots_per_factor):
        v_cand = CRT(list(combo), factors)
        e_cand = int(v_cand[0])
        e_candidates.append(e_cand)

    K = CyclotomicField(11)
    z = K.gen()
    automs = K.automorphisms()
    pr = K.ideal(p).factor()

    P1 = pr[0][0]
    I = K.ideal(1)
    for a in range(1, 11):
        if a >= 6:
            sig = [s for s in automs if s(z) == z**a][0]
            I = I * sig(P1)

    gen = I.gens_reduced()[0]

    candidate_orders = set()
    for u in [-1, 1]:
        for k in range(11):
            r = u * (z**k) * gen
            ord_cand = ZZ(prod([ (1 - s(r)) for s in automs ]))
            candidate_orders.add(ord_cand)

    for N in candidate_orders:
        for e_val in e_candidates:
            if gcd(e_val, N) == 1:
                d = inverse_mod(e_val, N)
                P = d * ct
                if P[0].degree() == 1:
                    x0 = -P[0][0]
                    flag_bytes = long_to_bytes(int(x0))
                    if b"NNS{" in flag_bytes or b"NSS{" in flag_bytes:
                        flag = flag_bytes.decode()
                        print("FLAG:", flag)
                        with open("../flag.txt", "w") as out_f:
                            out_f.write(flag + "\n")
                        return flag

if __name__ == "__main__":
    solve()
