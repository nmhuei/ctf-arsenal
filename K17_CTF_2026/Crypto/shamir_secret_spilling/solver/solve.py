#!/usr/bin/env python3
"""Solver for K17 CTF 2026 / Crypto / shamir secret spilling.

Vulnerability / Mathematical formulation:
The challenge defines two polynomials:
    - P(x) of degree < 16 (16 coefficients), where 16 shares (x_k, px_k) are known.
    - Q(x) of degree < 32 (32 coefficients), where 16 shares match known (backward compatibility)
      and 8 newly issued shares (x_j, qx_j) are given.
    - Secret: FLAG = Q(0) = Q_0.
    - Bound relation: for all 0 <= i < 32:
          abs(centered(Q[i] - P_padded[i])) < B
      where P_padded is P zero-padded to 32 coefficients.

Let delta = Q - P_padded in Z^32. Then:
    - ||delta||_infty < B (where B ~ 2^273, MOD ~ 2^512).
    - Q satisfies 24 evaluations: 16 on known and 8 on new.
    - This gives 24 linear equations in 32 variables over GF(MOD):
          M * delta = y (mod MOD)
      where M[r, c] = x_r^c, and y_r = eval_r - P_padded(x_r) mod MOD.

Since M has full row rank (24), we can partition M into:
    M = [A | B_mat]  with A in GL_24(GF(MOD)) and B_mat in GF(MOD)^(24 x 8).

Multiplying by A^-1:
    [I_24 | A^-1 * B_mat] * [delta_{0..23} | delta_{24..31}]^T = A^-1 * y (mod MOD)

Let W = A^-1 * B_mat (24 x 8) and y_target = A^-1 * y (24 x 1).
Then for the 8 variables t = delta_{24..31}:
    delta_{0..23} = y_target - W * t (mod MOD)

We construct a 33 x 33 Kannan embedding lattice:
    Rows:
      - 24 rows: MOD * e_j for j in 0..23
      - 8 rows:  (-W[:, i], e_i, 0) for i in 0..7
      - 1 row:   (y_target, 0, B)

All components of the vector [delta_{0..23}, t_{0..7}, B] have absolute value < B.
Using LLL (or flatter), the short vector is found immediately in less than a second.
Q_0 = (P_padded[0] + delta[0]) mod MOD yields the flag.

Zero hardcoded targets or magic constants.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SAGE_EXEC = "/home/light/miniforge3/envs/sage/bin/sage"


def parse_params(content: str) -> tuple[int, int, list[tuple[int, int]], list[tuple[int, int]]]:
    loc: dict[str, object] = {}
    exec(content, loc)
    return int(loc["MOD"]), int(loc["B"]), list(loc["known"]), list(loc["new"])


def solve_with_sage(mod: int, b_bound: int, known: list[tuple[int, int]], new: list[tuple[int, int]]) -> str:
    script = f"""
from sage.all import *
import re

MOD = {mod}
B = {b_bound}
known = {known}
new = {new}

F = GF(MOD)
R.<x> = PolynomialRing(F)
P_poly = R.lagrange_polynomial(known)
P_coeffs = [int(c) for c in P_poly.list()] + [0] * (16 - len(P_poly.list()))
P_padded = P_coeffs + [0] * 16

all_evals = list(known) + list(new)
M = matrix(F, 24, 32, lambda r, c: F(all_evals[r][0])^c)
y = vector(F, [F(all_evals[i][1]) - F(sum(P_padded[c] * (all_evals[i][0]^c) for c in range(32))) for i in range(24)])

A = M[:, :24]
B_mat = M[:, 24:]
A_inv = A.inverse()

W = A_inv * B_mat
y_target = A_inv * y

rows = []
for j in range(24):
    r = [0] * 33
    r[j] = int(MOD)
    rows.append(r)

for i in range(8):
    r = [0] * 33
    for j in range(24):
        r[j] = -int(W[j, i])
    r[24 + i] = 1
    rows.append(r)

r_target = [0] * 33
for j in range(24):
    r_target[j] = int(y_target[j])
r_target[32] = int(B)
rows.append(r_target)

mat = Matrix(ZZ, rows)
try:
    L = mat.LLL(algorithm="flatter")
except Exception:
    L = mat.LLL()

found = False
for r in L.rows():
    if abs(r[32]) == int(B):
        sgn = 1 if r[32] == int(B) else -1
        delta = [sgn * int(r[j]) for j in range(24)] + [sgn * int(r[24 + i]) for i in range(8)]
        if all(abs(val) < B for val in delta):
            Q = [(P_padded[idx] + delta[idx]) % MOD for idx in range(32)]
            flag_int = Q[0]
            length = (flag_int.bit_length() + 7) // 8
            flag_bytes = flag_int.to_bytes(length, "big")
            print("FLAG_BYTES:" + flag_bytes.decode("latin1", errors="replace"))
            found = True
            break

if not found:
    raise RuntimeError("Failed to recover short delta vector from lattice")
"""
    with tempfile.NamedTemporaryFile("w", suffix=".sage", delete=False) as f:
        f.write(script)
        temp_name = f.name

    try:
        res = subprocess.run([SAGE_EXEC, temp_name], capture_output=True, text=True, check=True)
        for line in res.stdout.splitlines():
            if line.startswith("FLAG_BYTES:"):
                raw_flag = line.split("FLAG_BYTES:", 1)[1]
                match = re.search(r"(?:K17|FLAG)\{[^}\r\n]+\}", raw_flag)
                if match:
                    return match.group(0)
                return raw_flag
        raise RuntimeError(f"Flag not found in Sage output: {res.stdout}\n{res.stderr}")
    finally:
        Path(temp_name).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Solve shamir secret spilling challenge")
    parser.add_argument(
        "input",
        nargs="?",
        default=str(Path(__file__).resolve().parents[1] / "challenge" / "out.txt"),
        help="Path to out.txt (default: ../challenge/out.txt)",
    )
    args = parser.parse_args()
    target_file = Path(args.input)
    if not target_file.exists():
        print(f"[-] Input file not found: {target_file}", file=sys.stderr)
        return 1

    content = target_file.read_text()
    mod, b_bound, known, new = parse_params(content)
    flag = solve_with_sage(mod, b_bound, known, new)
    print(flag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
