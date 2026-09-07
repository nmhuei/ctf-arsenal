#!/usr/bin/env sage
from sage.all import *
from Crypto.Util.number import isPrime, long_to_bytes
import sys
from pathlib import Path

chal_dir = Path("/home/light/Workspace/CTF/NNS_CTF_2026/crypto/Light-Weight_Encryption/challenge/crypto_light-weight-encryption")
output_file = chal_dir / "output.py"

with open(output_file) as f:
    text = f.read()

ns = {}
exec(text, ns)
A = Matrix(ZZ, 112, 16, ns["pk"][0])
B = vector(ZZ, ns["pk"][1])
c1 = vector(ZZ, ns["ct"][0])
c2 = Integer(ns["ct"][1])
q = 2**768

print("[*] Computing left kernel of A...")
K = A.left_kernel().basis_matrix()
K_short = K.LLL(algorithm="flatter")

print("[*] Setting up Kannan CVP lattice to recover sk...")
k_eqs = 8
V = [(K_short[i] * B) % q for i in range(k_eqs)]
W = 2**(561 - 128)

rows = []
rows.append([W] + [int(v) for v in V])
for i in range(k_eqs):
    row = [0] * (k_eqs + 1)
    row[i + 1] = int(q)
    rows.append(row)

lat = Matrix(ZZ, rows)
lat_red = lat.LLL(algorithm="flatter")

sk = None
for vec in lat_red.rows():
    if vec[0] != 0:
        cand = abs(vec[0]) // W
        if isPrime(cand) and 125 <= cand.bit_length() <= 130:
            sk = cand
            break

assert sk is not None, "Failed to recover sk"
print(f"[+] Recovered sk = {sk}")

print("[*] Recovering p...")
KB = vector(ZZ, [(sk * b) % q for b in B])
K_KB = K_short * KB
p_cands = []
for val in K_KB:
    v = Integer(val % q)
    if v > q // 2:
        v -= q
    p_cands.append(abs(v))

from math import gcd
p = p_cands[0]
for val in p_cands[1:]:
    p = gcd(p, val)

for p_factor, _ in factor(p):
    if isPrime(p_factor) and p_factor.bit_length() > 500:
        p = p_factor
        break

assert isPrime(p), "Failed to isolate prime p"
print(f"[+] Recovered p = {p}")

print("[*] Computing integer left inverse L of A...")
D, U, V = A.smith_form()
D_inv = Matrix(ZZ, 16, 112)
for i in range(16):
    D_inv[i, i] = 1
L = V * D_inv * U
assert L * A == identity_matrix(ZZ, 16)

print("[*] Reconstructing error vector and target syndrome...")
K_orig = A.left_kernel().basis_matrix()
KB_orig = vector(ZZ, [(sk * b) % q for b in B])
K_KB_orig = K_orig * KB_orig
E = []
for val in K_KB_orig:
    v = Integer(val % q)
    if v > q // 2:
        v -= q
    E.append(v // p)
E = vector(ZZ, E)

D_K, U_K, V_K = K_orig.smith_form()
UE = U_K * E
y = []
for i in range(D_K.nrows()):
    d = D_K[i, i]
    if d != 0:
        y.append(UE[i] // d)
    else:
        y.append(0)
while len(y) < D_K.ncols():
    y.append(0)
y = vector(ZZ, y)
e0 = V_K * y

A_cols = A.columns()
M_rows = [list(c) + [0] for c in A_cols] + [list(e0) + [1]]
M = Matrix(ZZ, M_rows)
M_red = M.LLL(algorithm="flatter")

e_small = None
for r in M_red.rows():
    if abs(r[-1]) == 1:
        sgn = r[-1]
        cand = vector(ZZ, [sgn * x for x in r[:-1]])
        if K_orig * cand == E:
            e_small = cand
            break

if e_small is None:
    e_small = e0

print("[*] Performing Compact-LWE algebraic decryption...")
rhs = vector(ZZ, [(sk * B[i] - p * e_small[i]) % q for i in range(112)])
S_prime = vector(ZZ, [(L * rhs)[i] % q for i in range(16)])

val = (sk * c2 + c1 * S_prime) % q
val_int = Integer(val)
if val_int > q // 2:
    val_int -= q

pt = (inverse_mod(sk, p) * (val_int % p)) % p
flag = long_to_bytes(int(pt))
print(f"[+] FLAG: {flag.decode(errors='ignore')}")
