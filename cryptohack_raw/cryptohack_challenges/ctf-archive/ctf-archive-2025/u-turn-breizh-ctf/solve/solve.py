#!/usr/bin/env python3
from ast import literal_eval
from pathlib import Path

try:
    from z3 import Int, Solver, Sum, sat
except ImportError:
    raise SystemExit("Missing dependency: pip install z3-solver")

HERE = Path(__file__).resolve().parent
A = literal_eval((HERE / "A.txt").read_text())
h = bytes.fromhex((HERE / "output.txt").read_text().strip())

k, l, n = 48, 50, 256
charset = [-2, -1, 0, 1, 2]

# Recover the 50 balanced base-5 digits x such that A*x == h (mod 256).
x = [Int(f"x{i}") for i in range(l)]
s = Solver()
for xi in x:
    s.add(xi >= -2, xi <= 2)
for row, target in zip(A, h):
    s.add(Sum([row[i] * x[i] for i in range(l)]) % n == target)

if s.check() != sat:
    raise SystemExit("No solution found")

m = s.model()
digits = [m[xi].as_long() for xi in x]

# Invert btq() for the known low 50 base-5 digits.  sanitize() truncates the
# quinary expansion, so brute-force the few missing high base-5 digits and keep
# the candidate whose bytes match the flag charset after XORing the PKCS#7 block.
low = sum((d + 2) * (5 ** i) for i, d in enumerate(digits))
step = 5 ** l
limit = 256 ** 16
hexchars = set(b"0123456789abcdef")

for val in range(low, limit, step):
    out = val.to_bytes(16, "little")
    msg = bytes(b ^ 0x10 for b in out)  # because the second padded block is 0x10*16
    if all(c in hexchars for c in msg):
        flag = b"BZHCTF{" + msg + b"}"
        print(flag.decode())
        break
else:
    raise SystemExit("No flag-like candidate found")
