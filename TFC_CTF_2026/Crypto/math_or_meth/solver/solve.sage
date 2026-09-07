#!/usr/bin/env sage
import os
import sys
import time
import numpy as np
from Crypto.Util.number import long_to_bytes

CHALL_DIR = '/home/light/Workspace/CTF/TFC_CTF_2026/Crypto/math_or_meth/challenge'
sys.path.insert(0, CHALL_DIR)
import output

p = output.p
h = output.h
n = output.n
m = output.m
B = output.B
base = B + 1

print(f"[+] Loaded parameters: n={n}, m={m}, B={B}, p={p.bit_length()} bits")

# Step 1: Orthogonal Lattice Reduction via flatter
print("[*] Step 1: Constructing orthogonal lattice L_p^perp(h)...")
t0 = time.time()
h0_inv = pow(h[0], -1, p)
rows = [[p] + [0]*(m-1)]
for j in range(1, m):
    r = [0]*m
    r[0] = (-h[j] * h0_inv) % p
    r[j] = 1
    rows.append(r)

M = Matrix(ZZ, rows)
print(f"[*] Running flatter LLL on {m}x{m} lattice...")
L = M.LLL(algorithm='flatter')
print(f"[+] Lattice reduced in {time.time() - t0:.2f}s")

# Extract short vectors orthogonal to A
short_vecs = [v for v in L.rows() if v.norm().n() < 15000]
print(f"[+] Found {len(short_vecs)} short vectors (expected {m - n} = {88 - 57} = 31)")
assert len(short_vecs) == m - n

V = Matrix(ZZ, short_vecs)
print("[*] Computing integer kernel Lambda...")
Lambda = V.right_kernel_matrix()
print(f"[+] Lambda dimension: {Lambda.nrows()}x{Lambda.ncols()}")
Lambda_lll = Lambda.LLL(algorithm='flatter')

# Step 2: Vectorized Babai Nearest Plane using QR
print("[*] Step 2: Running vectorized Babai Nearest Plane to recover rows of A...")
t1 = time.time()
B_mat = np.array(Lambda_lll, dtype=np.float64) # (57, 88)
dim, m_dim = B_mat.shape
Q, R = np.linalg.qr(B_mat.T) # Q: (88, 57), R: (57, 57) upper triangular

def run_babai_batch(targets):
    tQ = targets @ Q
    N = targets.shape[0]
    z = np.zeros((N, dim), dtype=np.int64)
    for i in reversed(range(dim)):
        val = (tQ[:, i] - z[:, i+1:] @ R[i, i+1:]) / R[i, i]
        z[:, i] = np.round(val)
    return z

N = 25000
targets = np.random.uniform(0, 32, size=(N, m_dim))
z = run_babai_batch(targets)
z_unique = np.unique(z, axis=0)

Lambda_exact = Matrix(ZZ, Lambda_lll)
recovered_flag = None

for zi in z_unique:
    pt = vector(ZZ, zi) * Lambda_exact
    if all(0 <= c <= 32 for c in pt):
        val = sum(int(pt[i]) * (base^i) for i in range(len(pt)))
        cand = long_to_bytes(val)
        if all(32 <= b <= 126 for b in cand) and len(cand) > 10:
            flag_str = f"TFCCTF{{{cand.decode('latin-1')}}}"
            print(f"[+] RECOVERED FLAG: {flag_str}")
            recovered_flag = flag_str
            break

print(f"[+] Step 2 completed in {time.time() - t1:.2f}s")

if recovered_flag:
    flag_file = '/home/light/Workspace/CTF/TFC_CTF_2026/Crypto/math_or_meth/flag.txt'
    with open(flag_file, "w") as f:
        f.write(recovered_flag + "\n")
    print(f"[+] Flag written to {flag_file}")
else:
    print("[-] Flag not found in this batch, try increasing N.")
