#!/usr/bin/env python3
"""Fixed-dimensional lifted constraints for the public instance only."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from lattice_relations import D_BOUND, gauss_reduce, kernel_basis, pair_bounds

ORDERED_PAIRS = ((0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1))


@dataclass(frozen=True)
class ModularConstraint:
    i: int
    j: int
    modulus: int
    determinant_linear: tuple[int, int]
    square_coeffs: tuple[int, int, int]
    residue_coeffs: tuple[int, int, int]


def lift_coordinates(lam: int, mu: int) -> tuple[int, int, int]:
    return lam * lam, lam * mu, mu * mu


def rank_one_ok(u: int, v: int, w: int) -> bool:
    return u >= 0 and w >= 0 and u * w == v * v


def lifted_bounds_ok(
    u: int,
    v: int,
    w: int,
    u_bound: int,
    abs_v_bound: int,
    w_bound: int,
) -> bool:
    return (
        0 <= u <= u_bound
        and abs(v) <= abs_v_bound
        and 0 <= w <= w_bound
    )


def small_residue_ok(residue: int, bound: int = D_BOUND) -> bool:
    return 0 <= residue <= bound


def determinant_linear_coeffs(
    r: Sequence[int], s: Sequence[int], i: int, j: int
) -> tuple[int, int]:
    if i == j or not (0 <= i < 3 and 0 <= j < 3):
        raise ValueError("expected distinct indices in {0,1,2}")

    if (i, j) == (0, 1):
        return int(r[2]), int(s[2])
    if (i, j) == (0, 2):
        return -int(r[1]), -int(s[1])
    if (i, j) == (1, 2):
        return int(r[0]), int(s[0])

    a, b = determinant_linear_coeffs(r, s, j, i)
    return -a, -b


def determinant_square_coeffs(
    r: Sequence[int], s: Sequence[int], i: int, j: int
) -> tuple[int, int, int]:
    R, S = determinant_linear_coeffs(r, s, i, j)
    return R * R, 2 * R * S, S * S


def residue_linear_coeffs(
    n: int,
    hints: Sequence[int],
    r: Sequence[int],
    s: Sequence[int],
    i: int,
    j: int,
) -> tuple[int, int, int]:
    if len(hints) != 3:
        raise ValueError("expected exactly three hints")

    h_i = int(hints[i])
    h_j = int(hints[j])
    if math.gcd(h_i, h_j) != 1:
        raise ValueError("h_j^2 is not invertible modulo h_i")

    alpha, beta, gamma = determinant_square_coeffs(r, s, i, j)
    scale = (-int(n) * pow((h_j * h_j) % h_i, -1, h_i)) % h_i
    return (
        (scale * alpha) % h_i,
        (scale * beta) % h_i,
        (scale * gamma) % h_i,
    )


def build_six_constraints(
    n: int, hints: Sequence[int], r: Sequence[int], s: Sequence[int]
) -> tuple[ModularConstraint, ...]:
    if len(hints) != 3:
        raise ValueError("expected exactly three hints")

    rows = []
    for i, j in ORDERED_PAIRS:
        rows.append(
            ModularConstraint(
                i=i,
                j=j,
                modulus=int(hints[i]),
                determinant_linear=determinant_linear_coeffs(r, s, i, j),
                square_coeffs=determinant_square_coeffs(r, s, i, j),
                residue_coeffs=residue_linear_coeffs(n, hints, r, s, i, j),
            )
        )
    return tuple(rows)


def evaluate_constraint(row: ModularConstraint, u: int, v: int, w: int) -> int:
    f_u, f_v, f_w = row.residue_coeffs
    return (f_u * u + f_v * v + f_w * w) % row.modulus


def evaluate_six(
    constraints: Iterable[ModularConstraint], u: int, v: int, w: int
) -> tuple[int, ...]:
    return tuple(evaluate_constraint(row, u, v, w) for row in constraints)


def small_residue_checks(
    constraints: Iterable[ModularConstraint],
    u: int,
    v: int,
    w: int,
    bound: int = D_BOUND,
) -> tuple[bool, ...]:
    return tuple(
        small_residue_ok(evaluate_constraint(row, u, v, w), bound)
        for row in constraints
    )


def relation_basis_for_hints(
    hints: Sequence[int],
) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    r0, s0, _ = kernel_basis(tuple(int(x) for x in hints))
    r, s, _ = gauss_reduce(r0, s0)
    return r, s


def concrete_lifted_bounds(
    r: Sequence[int], s: Sequence[int]
) -> tuple[int, int, int, int, int]:
    bounds = pair_bounds(tuple(r), tuple(s))
    lambda_bound = min(item["lambda_bound"] for item in bounds)
    mu_bound = min(item["mu_bound"] for item in bounds)
    return (
        lambda_bound,
        mu_bound,
        lambda_bound * lambda_bound,
        lambda_bound * mu_bound,
        mu_bound * mu_bound,
    )


def _solve_relation_coordinates(
    dvec: Sequence[int], r: Sequence[int], s: Sequence[int]
) -> tuple[int, int]:
    for j, k in ((0, 1), (0, 2), (1, 2)):
        delta = r[j] * s[k] - r[k] * s[j]
        if delta == 0:
            continue
        lam_num = dvec[j] * s[k] - dvec[k] * s[j]
        mu_num = r[j] * dvec[k] - r[k] * dvec[j]
        assert lam_num % delta == 0
        assert mu_num % delta == 0
        return lam_num // delta, mu_num // delta
    raise AssertionError("rank-two basis has no nonzero 2x2 minor")


def run_self_tests() -> None:
    p, q = 101, 113
    coeffs = ((1, 1), (1, 2), (1, 4))
    hints = tuple(a * p + b * q for a, b in coeffs)
    n = p * q

    assert all(
        math.gcd(hints[i], hints[j]) == 1
        for i, j in ORDERED_PAIRS
    )

    r, s = relation_basis_for_hints(hints)
    d01 = coeffs[0][0] * coeffs[1][1] - coeffs[1][0] * coeffs[0][1]
    d02 = coeffs[0][0] * coeffs[2][1] - coeffs[2][0] * coeffs[0][1]
    d12 = coeffs[1][0] * coeffs[2][1] - coeffs[2][0] * coeffs[1][1]
    dvec = (d12, -d02, d01)
    assert sum(dvec[k] * hints[k] for k in range(3)) == 0

    lam, mu = _solve_relation_coordinates(dvec, r, s)
    u, v, w = lift_coordinates(lam, mu)
    assert rank_one_ok(u, v, w)
    assert not rank_one_ok(u, v + 1, w)

    rows = build_six_constraints(n, hints, r, s)
    assert len(rows) == 6
    residues = evaluate_six(rows, u, v, w)
    expected = tuple(coeffs[i][0] * coeffs[i][1] for i, _ in ORDERED_PAIRS)
    assert residues == expected

    synthetic_bound = max(max(pair) for pair in coeffs) ** 2
    assert all(small_residue_checks(rows, u, v, w, synthetic_bound))

    row_map = {(row.i, row.j): row for row in rows}
    for i, j in ((0, 1), (0, 2), (1, 2)):
        fwd = row_map[(i, j)]
        rev = row_map[(j, i)]
        assert rev.determinant_linear == tuple(
            -x for x in fwd.determinant_linear
        )
        assert rev.square_coeffs == fwd.square_coeffs

    print("PASS synthetic: lift/rank-one identity")
    print("PASS synthetic: six modular residues equal exact A_i values")
    print("PASS synthetic: small-residue bounds")
    print("PASS synthetic: ordered-pair determinant sign/square consistency")

    data = json.loads(Path("INSTANCE.json").read_text())
    public_n = int(data["n"])
    public_hints = tuple(int(x) for x in data["hints"])

    assert len(public_hints) == 3
    assert all(
        math.gcd(public_hints[i], public_hints[j]) == 1
        for i, j in ORDERED_PAIRS
    )

    public_r, public_s = relation_basis_for_hints(public_hints)
    public_rows = build_six_constraints(
        public_n, public_hints, public_r, public_s
    )

    assert tuple((row.i, row.j) for row in public_rows) == ORDERED_PAIRS
    assert tuple(row.modulus for row in public_rows) == tuple(
        public_hints[i] for i, _ in ORDERED_PAIRS
    )

    for row in public_rows:
        assert len(row.residue_coeffs) == 3
        assert all(0 <= x < row.modulus for x in row.residue_coeffs)

    lb, mb, ub, vb, wb = concrete_lifted_bounds(public_r, public_s)
    assert lb > 0 and mb > 0
    assert ub == lb * lb
    assert vb == lb * mb
    assert wb == mb * mb

    assert lifted_bounds_ok(0, 0, 0, ub, vb, wb)
    assert rank_one_ok(0, 0, 0)

    zero_residues = evaluate_six(public_rows, 0, 0, 0)
    assert zero_residues == (0,) * 6
    assert all(small_residue_checks(public_rows, 0, 0, 0))

    print("PASS public: six fixed-dimensional modular rows constructed")
    print("PASS public: canonical residue coefficients and moduli")
    print(
        "PASS public: concrete lifted bounds",
        {
            "lambda_bits": lb.bit_length(),
            "mu_bits": mb.bit_length(),
            "u_bits": ub.bit_length(),
            "abs_v_bits": vb.bit_length(),
            "w_bits": wb.bit_length(),
            "residue_bound_bits": D_BOUND.bit_length(),
        },
    )
    print("PASS public: rank-one/small-residue check functions exercised")
    print("ALL_TESTS_PASS")


if __name__ == "__main__":
    run_self_tests()
