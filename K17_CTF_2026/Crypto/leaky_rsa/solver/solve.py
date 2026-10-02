#!/usr/bin/env python3
"""Solver for K17 CTF 2026 / Crypto / leaky rsa.

Vulnerability / Algebraic relation:
The challenge provides:
    N = P * Q
    e = 257
    leak = dp + dq
    c = pow(m, e, N)

By definition of RSA CRT exponents:
    e * dp = k * (P - 1) + 1  for some 1 <= k < e
    e * dq = j * (Q - 1) + 1  for some 1 <= j < e

Summing both equations:
    e * leak = e * dp + e * dq
             = k * (P - 1) + j * (Q - 1) + 2
             = k * P + j * Q - (k + j) + 2

Let A = e * leak + (k + j) - 2 = (k * P) + (j * Q).
We also know that:
    (k * P) * (j * Q) = (k * j) * (P * Q) = k * j * N.

Therefore, (k * P) and (j * Q) are the positive integer roots of the quadratic equation:
    T^2 - A * T + (k * j * N) = 0

Discriminant:
    Delta = A^2 - 4 * k * j * N

Since 1 <= k, j < e (with e = 257, only 256 * 256 = 65,536 pairs), we can check
all possible pairs (k, j) in less than a second:
    1. If Delta >= 0 and is an integer square (isqrt(Delta)^2 == Delta).
    2. Compute T1 = (A + isqrt(Delta)) // 2, T2 = (A - isqrt(Delta)) // 2.
    3. Verify if (T1 % k == 0 and T2 % j == 0) or (T2 % k == 0 and T1 % j == 0).
    4. Verify P * Q == N.
    5. Recover phi = (P - 1) * (Q - 1), d = pow(e, -1, phi), and m = pow(c, d, N).

No target parameters, keys, or flags are hardcoded; all values are parsed
from the challenge files, command-line arguments, or standard input.
"""

from __future__ import annotations

import argparse
import math
import os
import re
import sys
from pathlib import Path


def parse_output(content: str) -> dict[str, int]:
    """Parse key = value integers from output file or text."""
    params: dict[str, int] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            digits = re.findall(r"\d+", val)
            if digits:
                params[key] = int(digits[0])
    return params


def int_to_bytes(n: int) -> bytes:
    """Convert a large integer to big-endian bytes."""
    length = (n.bit_length() + 7) // 8
    return n.to_bytes(length, "big")


def recover_factors(N: int, e: int, leak: int) -> tuple[int, int]:
    """Search for (k, j) in [1, e-1] to factor N via quadratic equation."""
    for k in range(1, e):
        for j in range(1, e):
            A = e * leak + k + j - 2
            disc = A * A - 4 * k * j * N
            if disc < 0:
                continue
            s = math.isqrt(disc)
            if s * s != disc:
                continue

            root1 = (A + s) // 2
            root2 = (A - s) // 2

            if root1 % k == 0 and root2 % j == 0:
                P = root1 // k
                Q = root2 // j
                if P * Q == N:
                    return P, Q

            if root2 % k == 0 and root1 % j == 0:
                P = root2 // k
                Q = root1 // j
                if P * Q == N:
                    return P, Q

    raise RuntimeError("failed to factor N with given parameters")


def solve(out_path_or_content: str | Path) -> str:
    """Solve the challenge given the path to out.txt or its content."""
    path = Path(out_path_or_content)
    if path.is_file():
        content = path.read_text()
    else:
        content = str(out_path_or_content)

    params = parse_output(content)
    for required in ("N", "e", "leak", "c"):
        if required not in params:
            raise ValueError(f"Missing required parameter {required!r} in input")

    N = params["N"]
    e = params["e"]
    leak = params["leak"]
    c = params["c"]

    P, Q = recover_factors(N, e, leak)
    phi = (P - 1) * (Q - 1)
    d = pow(e, -1, phi)
    m = pow(c, d, N)
    flag_bytes = int_to_bytes(m)

    match = re.search(r"(?:K17|FLAG)\{[^}\r\n]+\}", flag_bytes.decode("latin1", errors="ignore"))
    if match:
        return match.group(0)
    return flag_bytes.decode("latin1", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description="Solve leaky rsa challenge")
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

    flag = solve(target_file)
    print(flag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
