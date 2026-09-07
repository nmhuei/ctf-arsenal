#!/usr/bin/env python3
import json
from pathlib import Path

from lifted_constraints import (
    build_six_constraints,
    concrete_lifted_bounds,
    evaluate_six,
    lift_coordinates,
    lifted_bounds_ok,
    rank_one_ok,
    relation_basis_for_hints,
    small_residue_checks,
)

MAX_EXHAUSTIVE_PAIRS = 10_000_000


def exact_square_equalities(rows, lam, mu, u, v, w):
    for row in rows:
        R, S = row.determinant_linear
        a, b, c = row.square_coeffs
        d = R * lam + S * mu
        if d * d != a * u + b * v + c * w:
            return False
    return True


def main():
    data = json.loads(Path("INSTANCE.json").read_text())
    n = int(data["n"])
    hints = tuple(int(x) for x in data["hints"])

    r, s = relation_basis_for_hints(hints)
    rows = build_six_constraints(n, hints, r, s)
    lb, mb, ub, vb, wb = concrete_lifted_bounds(r, s)

    lambda_count = 2 * lb + 1
    mu_count = 2 * mb + 1
    pair_count = lambda_count * mu_count

    result = {
        "complete": False,
        "bounds": {
            "lambda": lb,
            "mu": mb,
            "u": ub,
            "abs_v": vb,
            "w": wb,
        },
        "coordinate_pair_count": pair_count,
        "coordinate_pair_count_bits": pair_count.bit_length(),
        "records": [],
        "blocker": None,
    }

    if pair_count > MAX_EXHAUSTIVE_PAIRS:
        result["blocker"] = (
            "Exact exhaustive enumeration is infeasible: "
            f"{pair_count} bounded (lambda, mu) pairs "
            f"({pair_count.bit_length()} bits) exceed local cap "
            f"{MAX_EXHAUSTIVE_PAIRS}."
        )
        Path("RELATION_RESULTS.json").write_text(
            json.dumps(result, indent=2) + "\n"
        )
        print("BLOCKED:", result["blocker"])
        print("records = 0")
        print("complete = False")
        return 2

    survivors = []
    for lam in range(-lb, lb + 1):
        for mu in range(-mb, mb + 1):
            u, v, w = lift_coordinates(lam, mu)

            if not (u == lam * lam and v == lam * mu and w == mu * mu):
                continue
            if not rank_one_ok(u, v, w):
                continue
            if not lifted_bounds_ok(u, v, w, ub, vb, wb):
                continue
            if not exact_square_equalities(rows, lam, mu, u, v, w):
                continue

            residues = evaluate_six(rows, u, v, w)
            checks = small_residue_checks(rows, u, v, w)
            if not all(checks):
                continue

            survivors.append(
                {
                    "lambda": lam,
                    "mu": mu,
                    "u": u,
                    "v": v,
                    "w": w,
                    "residues": list(residues),
                }
            )

    result["complete"] = True
    result["records"] = survivors
    Path("RELATION_RESULTS.json").write_text(json.dumps(result, indent=2) + "\n")
    print("records =", len(survivors))
    print("complete = True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
