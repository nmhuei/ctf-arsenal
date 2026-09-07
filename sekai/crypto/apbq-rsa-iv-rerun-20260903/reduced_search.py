#!/usr/bin/env python3
"""Micro-step 3C3: exact elimination/reduction check.

This program intentionally reads only the allowed step artifacts.  It tests the
smallest plausible dimension reduction: eliminate the unknown small residues
A_i by comparing the two ordered-pair equations for each hint modulus.

 On the exact relation lattice, those three congruences collapse to identical
0 = 0 rows.  The script proves this on the recorded integers and reports that
the allowed artifacts do not contain the instantiated n-dependent rows needed
for a non-trivial modular-kernel or BDD lattice.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ALLOWED = (
    "STEP3C2.md",
    "RELATION_RESULTS.json",
   "lattice_relations.py",
   "lifted_constraints.py",
    "STEP3B.md",
   "STEP3C1.md",
)


def read_allowed():
    return {name: Path(name).read_text() for name in ALLOWED}


def parse_step3b(text):
    def literal(name):
        m = re.search(rf"^{re.escape(name)} = (.+)$", text, re.MULTILINE)
        if not m:
            raise RuntimeError(f"missing {name}")
        return ast.literal_eval(m.group(1))

    def integer(name):
        m = re.search(rf"^{re.escape(name)} = ([0-9]+)$", text, re.MULTILINE)
        if not m:
            raise RuntimeError(f"missing {name}")
        return int(m.group(1))

    return {
        "r": tuple(map(int, literal("reduced_basis_r"))),
        "s": tuple(map(int, literal("reduced_basis_s"))),
        "h": tuple(map(int, literal("primitive_hint_vector"))),
        "lambda_bound": integer("final_lambda_bound"),
        "mu_bound": integer("final_mu_bound"),
        "u_bound": integer("u_bound"),
        "v_bound": integer("abs_v_bound"),
        "w_bound": integer("w_bound"),
    }


def determinant_linear(r, s, i, j):
    if (i, j) == (0, 1):
        return r[2], s[2]
    if (i, j) == (0, 2):
        return -r[1], -s[1]
    if (i, j) == (1, 2):
        return r[0], s[0]
    if i == j:
        raise ValueError("distinct indices required")
    a, b = determinant_linear(r, s, j, i)
    return -a, -b


def square_coeffs(pair):
    a, b = pair
    return a * a, 2 * a * b, b * b



def eliminate_small_residues(h, r, s):
    """Compare the two A_i rows for each fixed i.

    If one cancels the common -n factor, the candidate row is
        h_k^2 d_ij^2 - h_j^2 d_ik^2 == 0 (mod h_i).
    It returns the coefficients in (u,v,w) canonically mod h_i.
    """
    rows = []
    for i in range(3):
        j, k = [t for t in range(3) if t != i]
        qij = square_coeffs(determinant_linear(r, s, i, j))
        qik = square_coeffs(determinant_linear(r, s, i, k))
        c = tuple(
            (h[k] * h[k] * qij[t] - h[j] * h[j] * qik[t]) % h[i]
            for t in range(3)
        )
        rows.append((i, j, k, h[i], c))
    return rows


def synthetic_identity_test():
    p, q = 101, 113
    coeffs = ((1, 1), (1, 2), (1, 4))
    h = tuple(a * p + b * q for a, b in coeffs)
    for i in range(3):
        j, k = [t for t in range(3) if t != i]
        dij = coeffs[i][0] * coeffs[j][1] - coeffs[j][0] * coeffs[i][1]
        dik = coeffs[i][0] * coeffs[k][1] - coeffs[k][0] * coeffs[i][1]
        assert (h[k] * h[k] * dij * dij - h[j] * h[j] * dik * dik) % h[i] == 0


def find_numeric_n(files):
    """Detect whether an allowed artifact records a concrete public n."""
    patterns = (
        re.compile(r"^\s*n\s*=\s*([0-9]{100,})\s+$", re.MULTILINE),
        re.compile(r"^\s*public_n\s*=\s*([0-9]{100,})\s+$", re.MULTILINE),
    )
    hits = []
    for name, text in files.items():
        for pat in patterns:
            for m in pat.finditer(text):
                hits.append((name, int(m.group(1))))
    return hits


def main():
    files = read_allowed()
    data = parse_step3b(files["STEP3B.md"])
    results = json.loads(files["RELATION_RESULTS.json"])
    synthetic_identity_test()

    rows = eliminate_small_residues(data["h"], data["r"], data["s"])
    print("PASS synthetic cancellation identity")
    print("METHOD=eliminate_A_i_then_modular_kernel_reduction")
    nonzero = 0
    for i, j, k, m, c in rows:
        is_zero = all(z == 0 for z in c)
        nonzero += not is_zero
        print(
            "row", (i, j, k),
            "modulus_bits", m.bit_length(),
            "coefficients", c,
            "identically_zero", is_zero,
        )

    print("nonzero_eliminated_rows =", nonzero)
    print("coordinate_pair_count_bits =", results["coordinate_pair_count_bits"])
    n_hits = find_numeric_n(files)
    print("concrete_numeric_n_assignments_in_allowed_artifacts =", len(n_hits))


    # Prove the actual blocker explicitly.
    if nonzero == 0 and len(n_hits) == 0:
        print("REDUCTION_RESULT=DEGENERATE_KERNEL_NO_INSTANTIATED_ROWS")
        print(
            "concrete_blocker = eliminating the three small A_i residues produces "
            "only identically zero congruences on the exact relation basis; "
            "the allowed artifacts record the symbolic n-dependent rows but no "
            "concrete n or instantiated residue-coefficient rows."
        )
        print(
            "next_smallest_local_experiment = supply only the three instantiated "
            "independent residue coefficient rows (or equivalently the concrete public n) "
            "as a sanitized local artifact, then run a scaled 6D low-residue lattice "
            "LLL/BKZ with x=(u,v,w) scaled by 2^399 to match the 2^1248 residue bound."
        )
        return 2

    print("REDUCTION_RESULT=UNEXPECTED: non-zero homogeneous row or numeric n found")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
