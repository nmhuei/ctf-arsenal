#!/usr/bin/env python3
"""
Solver for DownUnderCTF/CryptoHack "Substitution Cipher III".

Usage:
    python3 solve_substitution_cipher_iii.py output.txt

It recovers bilinear Matsumoto-Imai relations of the public map, substitutes
ciphertext bits, solves the resulting linear systems, and filters real/public-key
preimages that decode to printable ASCII.
"""
from __future__ import annotations

import sys
from itertools import combinations, product
from pathlib import Path

N = 80


def parse_poly(poly: str) -> set[tuple[int, ...]]:
    poly = poly.strip()
    if poly == "0":
        return set()
    out: set[tuple[int, ...]] = set()
    for term in poly.split(" + "):
        if term == "1":
            mono: tuple[int, ...] = ()
        else:
            mono = tuple(sorted({int(factor[1:]) for factor in term.split("*")}))
        # coefficients are in GF(2)
        if mono in out:
            out.remove(mono)
        else:
            out.add(mono)
    return out


def split_pubkey(line: str) -> list[set[tuple[int, ...]]]:
    s = line.strip()
    if not (s.startswith("(") and s.endswith(")")):
        raise ValueError("expected Sage tuple/vector on first line")
    parts = s[1:-1].split(", ")
    if len(parts) != N:
        raise ValueError(f"expected {N} public polynomials, got {len(parts)}")
    return [parse_poly(p) for p in parts]


def build_monomial_index() -> dict[tuple[int, ...], int]:
    idx: dict[tuple[int, ...], int] = {(): 0}
    for degree in (1, 2, 3):
        for mono in combinations(range(N), degree):
            idx[mono] = len(idx)
    return idx


def poly_to_int(poly: set[tuple[int, ...]], idx: dict[tuple[int, ...], int]) -> int:
    v = 0
    for mono in poly:
        v ^= 1 << idx[mono]
    return v


def mul_x_poly_to_int(i: int, poly: set[tuple[int, ...]], idx: dict[tuple[int, ...], int]) -> int:
    v = 0
    for mono in poly:
        # Boolean ring: x_i^2 = x_i
        if i in mono:
            out_mono = mono
        else:
            out_mono = tuple(sorted(mono + (i,)))
        v ^= 1 << idx[out_mono]
    return v


def find_bilinear_relations(polys: list[set[tuple[int, ...]]]) -> list[int]:
    """
    Find dependencies among columns representing:
        x_i*y_j, x_i, y_j, 1
    after substituting y_j = public_poly_j(x).

    A dependency is a relation in x/y variables that vanishes on the graph of the
    public key. For Matsumoto-Imai, these become linear equations in x once y is
    fixed to the ciphertext.
    """
    idx = build_monomial_index()
    poly_bits = [poly_to_int(p, idx) for p in polys]
    var_bits = [1 << idx[(i,)] for i in range(N)]

    basis: dict[int, tuple[int, int]] = {}  # pivot row -> (column vector, combination)
    deps: list[int] = []

    def add_column(v: int, comb: int) -> None:
        while v:
            pivot = v.bit_length() - 1
            if pivot in basis:
                bv, bc = basis[pivot]
                v ^= bv
                comb ^= bc
            else:
                basis[pivot] = (v, comb)
                return
        deps.append(comb)

    col = 0
    for i in range(N):
        for j in range(N):
            add_column(mul_x_poly_to_int(i, polys[j], idx), 1 << col)
            col += 1

    for i in range(N):
        add_column(var_bits[i], 1 << col)
        col += 1

    for j in range(N):
        add_column(poly_bits[j], 1 << col)
        col += 1

    add_column(1, 1 << col)
    return deps


def relation_to_linear_equation(dep: int, y_bits: str) -> int:
    """Return one GF(2) linear row in x bits; bit N stores the constant."""
    y = [int(c) for c in y_bits]
    row = 0
    constant = 0
    d = dep
    while d:
        lsb = d & -d
        k = lsb.bit_length() - 1
        if k < N * N:
            i, j = divmod(k, N)
            if y[j]:
                row ^= 1 << i
        elif k < N * N + N:
            row ^= 1 << (k - N * N)
        elif k < N * N + 2 * N:
            j = k - (N * N + N)
            if y[j]:
                constant ^= 1
        else:
            constant ^= 1
        d ^= lsb
    if constant:
        row ^= 1 << N
    return row


def rref(rows: list[int]) -> dict[int, int]:
    basis: dict[int, int] = {}
    mask = (1 << N) - 1
    for row in rows:
        r = row
        while r & mask:
            pivot = (r & mask).bit_length() - 1
            if pivot in basis:
                r ^= basis[pivot]
            else:
                basis[pivot] = r
                break
        else:
            if (r >> N) & 1:
                raise ValueError("linear system is inconsistent")

    for pivot in sorted(basis, reverse=True):
        row = basis[pivot]
        for other in list(basis):
            if other != pivot and ((basis[other] >> pivot) & 1):
                basis[other] ^= row
    return basis


def bits_to_bytes(sol: int) -> bytes:
    out = []
    for k in range(0, N, 8):
        b = 0
        for t in range(8):
            b = (b << 1) | ((sol >> (k + t)) & 1)
        out.append(b)
    return bytes(out)


def eval_pub(polys: list[set[tuple[int, ...]]], sol: int) -> str:
    bits = [(sol >> i) & 1 for i in range(N)]
    out = []
    for poly in polys:
        val = 0
        for mono in poly:
            prod = 1
            for i in mono:
                prod &= bits[i]
                if not prod:
                    break
            val ^= prod
        out.append(str(val))
    return "".join(out)


def solve_ciphertext(polys: list[set[tuple[int, ...]]], deps: list[int], ct: str) -> list[bytes]:
    basis = rref([relation_to_linear_equation(dep, ct) for dep in deps])
    pivots = set(basis)
    free = [i for i in range(N) if i not in pivots]

    candidates: list[bytes] = []
    for values in product([0, 1], repeat=len(free)):
        sol = 0
        for i, b in zip(free, values):
            if b:
                sol |= 1 << i
        for pivot, row in basis.items():
            val = ((row >> N) & 1) ^ ((row & sol).bit_count() & 1)
            if val:
                sol |= 1 << pivot
            else:
                sol &= ~(1 << pivot)
        if eval_pub(polys, sol) == ct:
            candidates.append(bits_to_bytes(sol))
    return candidates


def printable_ascii(bs: bytes) -> bool:
    return all(0x20 <= b <= 0x7e for b in bs)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 solve_substitution_cipher_iii.py output.txt")

    lines = Path(sys.argv[1]).read_text().strip().splitlines()
    if len(lines) != 3:
        raise ValueError("expected output file with 3 lines: pubkey, ct1, ct2")

    polys = split_pubkey(lines[0])
    ct1, ct2 = lines[1].strip(), lines[2].strip()
    deps = find_bilinear_relations(polys)

    cands1 = solve_ciphertext(polys, deps, ct1)
    cands2 = solve_ciphertext(polys, deps, ct2)

    print("ct1 candidates:", cands1)
    print("ct2 candidates:", cands2)

    m1 = next(c for c in cands1 if printable_ascii(c))
    m2 = next(c for c in cands2 if printable_ascii(c))
    print("FLAG:", f"DUCTF{{{(m1 + m2).decode()}}}")


if __name__ == "__main__":
    main()
