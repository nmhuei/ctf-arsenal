#!/usr/bin/env python3
"""C4 review experiment: exact 3D kernel from repeated-residue elimination.

Concrete instance data is parsed only from STEP3B.md and RELATION_RESULTS.json.
"""
from __future__ import annotations

import ast
import json
import math
import re
from pathlib import Path

from fpylll import IntegerMatrix, LLL


def parse_assignment(text: str, name: str):
    m = re.search(r"^" + re.escape(name) + r" = (.+)$", text, re.M)
    if not m:
        raise RuntimeError(f"missing {name} in STEP3B.md")
    return ast.literal_eval(m.group(1))


def egcd(a: int, b: int):
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


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B)))
             for j in range(len(B[0]))] for i in range(len(A))]


def transpose(A):
    return [list(row) for row in zip(*A)]


def det3(M):
    return (
        M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
        - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
        + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0])
    )


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def square_coeff(R: int, S: int):
    return (R * R, 2 * R * S, S * S)


def dlin(r, s, i, j):
    if (i, j) == (0, 1):
        return r[2], s[2]
    if (i, j) == (0, 2):
        return -r[1], -s[1]
    if (i, j) == (1, 2):
        return r[0], s[0]
    R, S = dlin(r, s, j, i)
    return -R, -S


def equal_residue_row(r, s, h, i):
    j, k = [q for q in range(3) if q != i]
    qj = square_coeff(*dlin(r, s, i, j))
    qk = square_coeff(*dlin(r, s, i, k))
    # Conditional nondegenerate reduction:
    # n*(d_ij^2*h_k^2 - d_ik^2*h_j^2) == 0 (mod h_i).
    # If gcd(n,h_i)=1, n cancels.
    return tuple(
        (qj[t] * pow(h[k], 2, h[i]) - qk[t] * pow(h[j], 2, h[i])) % h[i]
        for t in range(3)
    )


def row_to_gcd_transform(a):
    """Return unimodular U such that row(a)*U=(gcd(a),0,0)."""
    v = list(a)
    U = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    for j in (1, 2):
        aa, bb = v[0], v[j]
        if bb == 0:
            continue
        g, s, t = egcd(aa, bb)
        T = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        T[0][0] = s
        T[0][j] = -bb // g
        T[j][0] = t
        T[j][j] = aa // g
        v = [sum(v[k] * T[k][col] for k in range(3)) for col in range(3)]
        U = matmul(U, T)
    g = abs(v[0])
    if v[0] < 0:
        T = [[-1, 0, 0], [0, 1, 0], [0, 0, 1]]
        U = matmul(U, T)
        v[0] = -v[0]
    assert v == [g, 0, 0]
    assert abs(det3(U)) == 1
    assert [sum(a[k] * U[k][col] for k in range(3)) for col in range(3)] == [g, 0, 0]
    return U, g


def intersect_congruence(B, c, modulus):
    a = [dot(c, B[j]) for j in range(3)]
    U, g0 = row_to_gcd_transform(a)
    d = math.gcd(g0, modulus)
    index = modulus // d
    D = [[index, 0, 0], [0, 1, 0], [0, 0, 1]]
    B2 = matmul(matmul(D, transpose(U)), B)
    assert all(dot(c, row) % modulus == 0 for row in B2)
    assert abs(det3(B2)) == abs(det3(B)) * index
    return B2, index, d


def rank_one(x):
    u, v, w = x
    return u >= 0 and w >= 0 and u * w == v * v


def primitive_direction(x):
    g = math.gcd(math.gcd(abs(x[0]), abs(x[1])), abs(x[2]))
    if g == 0:
        return None
    y = tuple(v // g for v in x)
    if y[0] < 0 or (y[0] == 0 and y[2] < 0):
        y = tuple(-v for v in y)
    return y


def n2bits(x):
    return sum(v * v for v in x).bit_length()


def main():
    step = Path("STEP3B.md").read_text()
    rel = json.loads(Path("RELATION_RESULTS.json").read_text())

    r = tuple(parse_assignment(step, "reduced_basis_r"))
    s = tuple(parse_assignment(step, "reduced_basis_s"))
    h = tuple(parse_assignment(step, "primitive_hint_vector"))
    assert parse_assignment(step, "gcd_hints") == 1
    assert dot(r, h) == 0 and dot(s, h) == 0
    cr = cross(r, s)
    assert cr == h or cr == tuple(-x for x in h)

    rows = [equal_residue_row(r, s, h, i) for i in range(3)]

    B = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    indices = []
    image_gcds = []
    for i in range(3):
        B, idx, gd = intersect_congruence(B, rows[i], h[i])
        indices.append(idx)
        image_gcds.append(gd)

    det = abs(det3(B))
    assert det == math.prod(indices)

    M = IntegerMatrix(3, 3)
    for i in range(3):
        for j in range(3):
            M[i, j] = B[i][j]
    LLl.reduction(M, delta=0.999)
    RB = [tuple(int(M[i, j]) for j in range(3)) for i in range(3)]
    assert all(dot(rows[i], x) % h[i] == 0 for x in RB for i in range(3))

    bounds = rel["bounds"]
    ub = int(bounds["u"])
    vb = int(bounds["abs_v"])
    wb = int(bounds["w"])

    radius = 32
    tested = 0
    rank_one_hits = []
    directions = {}
    for a in range(-radius, radius + 1):
        for b in range(-radius, radius + 1):
            for c in range(-radius, radius + 1):
                if a == b == c == 0:
                    continue
                tested += 1
                x = tuple(a * RB[0][j] + b * RB[1][j] + c * RB[2][j] for j in range(3))
                if not rank_one(x):
                    continue
                bounded = x[0] <= ub and abs(x[1]) <= vb and x[2] <= wb
                rank_one_hits.append((sum(z*z for z in x), x, (a, b, c), bounded))
                y = primitive_direction(x)
                prev = directions.get(y)
                if prev is None or sum(z*z for z in x) < prev[0]:
                    directions[y] = (sum(z*z for z in x), x, (a, b, c), bounded)

    rank_one_hits.sort()
    bounded_hits = [hit for hit in rank_one_hits if hit[3]]

    print("PASS algebra_basis")
    print("modulus_bits", [x.bit_length() for x in h])
    print("intersection_index_bits", [x.bit_length() for x in indices])
    print("image_gcds", image_gcds)
    print("kernel_det_bits", det.bit_length())
    print("lll_norm2_bits", [n2bits(x) for x in RB])
    print("radius", radius)
    print("tested", tested)
    print("rank_one_hits", len(rank_one_hits))
    print("primitive_directions", len(directions))
    print("bounded_rank_one_hits", len(bounded_hits))
    if rank_one_hits:
        _, x, coeff, bounded = rank_one_hits[0]
        print("shortest_rank_one", x)
        print("shortest_coeff", coeff)
        print("shortest_bounded", bounded)
        print("shortest_coord_bits", [abs(z).bit_length() for z in x])
        print("shortest_primitive_direction", primitive_direction(x))
    print("REVIEW_REDUCTION_TEST_COMPLETE")


if __name__ == "__main__":
    main()
