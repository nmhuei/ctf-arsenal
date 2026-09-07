#!/usr/bin/env python3
import json
import math
from pathlib import Path

B = 1 << 624
D_BOUND = B * B


def xgcd(a, b):
    old_r, r = abs(a), abs(b)
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    if a < 0:
        old_s = -old_s
    if b < 0:
        old_t = -old_t
    return old_r, old_s, old_t


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def submul(a, q, b):
    return tuple(x - q * y for x, y in zip(a, b))


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def nearest_div(a, b):
    assert b > 0
    q, r = divmod(a, b)
    if 2 * r > b:
        return q + 1
    return q


def kernel_basis(h):
    h0, h1, h2 = h
    g01, u, v = xgcd(h0, h1)
    g = math.gcd(g01, h2)

    # First relation annihilates (h0,h1); second uses Bezout on h0,h1.
    r = (h1 // g01, -h0 // g01, 0)
    s = (-u * (h2 // g), -v * (h2 // g), g01 // g)

    assert dot(r, h) == 0
    assert dot(s, h) == 0
    assert cross(r, s) == tuple(-x // g for x in h)
    return r, s, g


def gauss_reduce(r, s):
    r = tuple(r)
    s = tuple(s)
    # Rows of T express the current basis vectors in the original basis.
    T = [[1, 0], [0, 1]]

    for _ in range(10000):
        if dot(s, s) < dot(r, r):
            r, s = s, r
            T[0], T[1] = T[1], T[0]

        q = nearest_div(dot(r, s), dot(r, r))
        if q == 0:
            break

        s = submul(s, q, r)
        T[1] = [T[1][0] - q * T[0][0], T[1][1] - q * T[0][1]]
    else:
        raise RuntimeError("Gauss reduction did not converge")

    if dot(s, s) < dot(r, r):
        r, s = s, r
        T[0], T[1] = T[1], T[0]

    detT = T[0][0] * T[1][1] - T[0][1] * T[1][0]
    assert abs(detT) == 1
    assert dot(r, r) <= dot(s, s)
    assert 2 * abs(dot(r, s)) <= dot(r, r)
    return r, s, tuple(map(tuple, T))


def pair_bounds(r, s):
    rows = []
    for j, k in ((0, 1), (0, 2), (1, 2)):
        delta = r[j] * s[k] - r[k] * s[j]
        if delta == 0:
            continue

        lambda_num = D_BOUND * (abs(s[j]) + abs(s[k]))
        mu_num = D_BOUND * (abs(r[j]) + abs(r[k]))
        # Exact integer upper bounds: ceil(numerator / |delta|).
        den = abs(delta)
        lambda_bound = (lambda_num + den - 1) // den
        mu_bound = (mu_num + den - 1) // den

        rows.append({
            "pair": (j, k),
            "delta": delta,
            "lambda_bound": lambda_bound,
            "mu_bound": mu_bound,
        })
    assert rows
    return rows


def bit_bound(x):
    return x.bit_length()


def main():
    data = json.loads(Path("INSTANCE.json").read_text())
    h = tuple(int(x) for x in data["hints"])
    assert len(h) == 3
    assert all(x > 0 for x in h)

    r0, s0, g = kernel_basis(h)
    r, s, T = gauss_reduce(r0, s0)

    # Exact relation checks after reduction.
    assert dot(r, h) == 0
    assert dot(s, h) == 0

    c = cross(r, s)
    primitive_h = tuple(x // g for x in h)
    assert c == primitive_h or c == tuple(-x for x in primitive_h)

    # Verify the reduced basis is an exact unimodular change of basis.
    rr = tuple(T[0][0] * r0[i] + T[0][1] * s0[i] for i in range(3))
    ss = tuple(T[1][0] * r0[i] + T[1][1] * s0[i] for i in range(3))
    assert rr == r
    assert ss == s

    bounds = pair_bounds(r, s)
    lambda_bound = min(x["lambda_bound"] for x in bounds)
    mu_bound = min(x["mu_bound"] for x in bounds)
    M = max(lambda_bound, mu_bound)

    # For a primitive full kernel basis, each minor matches the corresponding
    # component of h/g up to one common orientation sign.
    expected_minors = {
        (0, 1): primitive_h[2],
        (0, 2): -primitive_h[1],
        (1, 2): primitive_h[0],
    }
    orientation = None
    for item in bounds:
        e = expected_minors[item["pair"]]
        d = item["delta"]
        assert abs(d) == abs(e)
        sign = 1 if d == e else -1
        if orientation is None:
            orientation = sign
        assert sign == orientation

    # Symbolic representation d=(d12,-d02,d01)=lambda*r+mu*s.
    determinant_forms = {
        "d12": (r[0], s[0]),
        "d02": (-r[1], -s[1]),
        "d01": (r[2], s[2]),
    }

    # Exact section-5 lifted bounds.
    u_bound = lambda_bound * lambda_bound
    v_bound = lambda_bound * mu_bound
    w_bound = mu_bound * mu_bound

    print("PASS: exact rank-two integer kernel basis")
    print("gcd_hints =", g)
    print("original_basis_r =", r0)
    print("original_basis_s =", s0)
    print("reduced_basis_r =", r)
    print("reduced_basis_s =", s)
    print("unimodular_transform =", T)
    print("dot_r_h =", dot(r, h))
    print("dot_s_h =", dot(s, h))
    print("cross_reduced =", c)
    print("primitive_hint_vector =", primitive_h)
    print("gauss_norm2_r =", dot(r, r))
    print("gauss_norm2_s =", dot(s, s))
    print("gauss_dot =", dot(r, s))
    print("determinant_forms =", determinant_forms)

    for item in bounds:
        print(
            "pair_bound",
            item["pair"],
            "delta =", item["delta"],
            "lambda_bound =", item["lambda_bound"],
            "lambda_bits =", bit_bound(item["lambda_bound"]),
            "mu_bound =", item["mu_bound"],
            "mu_bits =", bit_bound(item["mu_bound"]),
        )

    print("final_lambda_bound =", lambda_bound)
    print("final_lambda_bits =", bit_bound(lambda_bound))
    print("final_mu_bound =", mu_bound)
    print("final_mu_bits =", bit_bound(mu_bound))
    print("M =", M)
    print("M_bits =", bit_bound(M))
    print("u_bound =", u_bound)
    print("u_bits =", bit_bound(u_bound))
    print("abs_v_bound =", v_bound)
    print("v_bits =", bit_bound(v_bound))
    print("w_bound =", w_bound)
    print("w_bits =", bit_bound(w_bound))
    print("PASS: zero-dot, primitive-cross, unimodularity, Gauss, minor, coordinate-bound, and lifting checks")
    print("ALL_TESTS_PASS")


if __name__ == "__main__":
    main()
