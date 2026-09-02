#!/usr/bin/env python3
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from fpylll import IntegerMatrix, LLL, CVP

PUB = "pubkey_e1a2fede0964b3adae6a6471bf1a2355.pem"
OUT = "output_1bae40aaa51fc17d22c19dd49f2bc971.txt"

with open(PUB, "rb") as f:
    key = load_pem_public_key(f.read())
n = key.public_numbers().n
e = key.public_numbers().e

ns = {}
with open(OUT, "r") as f:
    exec(f.read(), ns)
R = ns["R"]
c = int(ns["enc_flag"], 16)

k = (n.bit_length() + 7) // 8
B = 1 << (8 * (k - 2))
mid = (5 * B) // 2
rs = [1] + R
T = len(rs)
C = 1

# Lattice rows generate vectors:
#   (r_i*m - q_i*n, ..., C*m)
# Valid PKCS#1 v1.5 oracle answers imply every r_i*m mod n is in [2B, 3B),
# so the target is near (2.5B, ..., 2.5B, C*2.5B).
M = IntegerMatrix(T + 1, T + 1)
for i in range(T):
    M[i, i] = n
for j, r in enumerate(rs):
    M[T, j] = r
M[T, T] = C

LLL.reduction(M, delta=0.99, eta=0.501)
target = [mid] * T + [C * mid]
closest = CVP.babai(M, target)

candidates = set()
if closest[-1] % C == 0:
    candidates.add(closest[-1] // C)
    candidates.add(-closest[-1] // C)

for coord, r in zip(closest[:T], rs):
    inv = pow(r, -1, n)
    candidates.add((coord * inv) % n)
    candidates.add((-coord * inv) % n)

def valid(m):
    return pow(m, e, n) == c and all(2 * B <= (r * m) % n < 3 * B for r in rs)

for m in candidates:
    if 0 < m < n and valid(m):
        pt = m.to_bytes(k, "big")
        sep = pt.index(b"\x00", 2)
        print(pt[sep + 1:].decode())
        break
else:
    raise SystemExit("no valid plaintext recovered")
