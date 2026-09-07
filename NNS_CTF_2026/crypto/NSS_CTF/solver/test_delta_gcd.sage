from sage.all import *
import subprocess, time, re
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

t0 = time.time()
load("/home/light/Workspace/CTF/NNS_CTF_2026/crypto/NSS_CTF/challenge/crypto_nss-ctf/output.py")

n = 256
q = 367
P = next_prime(2^70)

Fp = GF(P)
Rp.<xp> = GF(P)[]
Sp = Rp.quotient(xp^n + 1)

def center(coeffs, m): return [((ZZ(c) + m//2) % m) - m//2 for c in coeffs]
def get_FD(idx):
    m, s = sigs[idx]
    s_cent = center(s, q)
    K_vec = [((m[i] - s_cent[i] + 1) % 3) - 1 for i in range(n)]
    F = [s_cent[i] + q * K_vec[i] for i in range(n)]
    Pq.<xq> = GF(q)[]
    Rq = Pq.quotient(xq^n + 1)
    pk_poly = Rq(pk)
    t = [ZZ(c) for c in (pk_poly * Rq(s)).lift().list()]
    while len(t) < n: t.append(0)
    t_cent = center(t, q)
    L = [((m[i] - t_cent[i] + 1) % 3) - 1 for i in range(n)]
    G = [t_cent[i] + q * L[i] for i in range(n)]
    return F, [(G[i] - F[i]) // 3 for i in range(n)]

F, D = get_FD(2)
Dp = Sp([int(c) % P for c in D])
Fp_elem = Sp([int(c) % P for c in F])
Hp = Fp_elem / Dp
h = [ZZ(c) for c in Hp.lift().list()]
while len(h) < n: h.append(0)

def convmat(coeffs):
    M = []
    for i in range(n):
        row = []
        for j in range(n):
            k = (i - j) % n
            c = coeffs[k]
            if i - j < 0: c = -c
            row.append(c)
        M.append(row)
    return Matrix(ZZ, M)

print("[*] Building 512x512 lattice...")
MT = convmat(h).transpose()
B = block_matrix(ZZ, [[P * identity_matrix(ZZ, n), zero_matrix(ZZ, n, n)], [-MT, identity_matrix(ZZ, n)]])
matrix_str = "[" + "\n".join("[" + " ".join(map(str, row)) + "]" for row in B) + "]"

print("[*] Running flatter on 512x512...")
t1 = time.time()
res = subprocess.run(["flatter"], input=matrix_str, text=True, capture_output=True)
print(f"[*] Flatter done in {time.time() - t1:.2f}s")

out = res.stdout.strip()
rows = []
for m in re.finditer(r"\[([-\d\s]+)\]", out):
    nums = [int(x) for x in m.group(1).split()]
    if len(nums) == 2 * n:
        rows.append(nums)

print(f"[*] Parsed {len(rows)} rows.")

# Extract the Delta parts of the top 5 shortest rows
# Each Delta part is an element of the ideal (Delta)
# Build the 256x256 ideal lattice spanned by shifts of the top delta rows!
delta_rows = []
for r in rows[:8]:
    d_part = r[n:]
    delta_rows.append(d_part)

print("[*] Building ideal lattice for Delta from top rows...")
M_delta = convmat(delta_rows[0])
for d_part in delta_rows[1:]:
    M_delta = M_delta.stack(convmat(d_part))

print(f"[*] M_delta shape: {M_delta.nrows()}x{M_delta.ncols()}")
print("[*] Computing HNF...")
t2 = time.time()
H_delta = M_delta.hermite_form(include_zero_rows=False)
print(f"[*] HNF computed in {time.time() - t2:.2f}s, shape: {H_delta.nrows()}x{H_delta.ncols()}")

matrix_str_256 = "[" + "\n".join("[" + " ".join(map(str, row)) + "]" for row in H_delta) + "]"
print("[*] Running flatter on 256x256 Delta ideal...")
t3 = time.time()
res2 = subprocess.run(["flatter"], input=matrix_str_256, text=True, capture_output=True)
print(f"[*] Flatter 256 done in {time.time() - t3:.2f}s")

out2 = res2.stdout.strip()
rows2 = []
for m in re.finditer(r"\[([-\d\s]+)\]", out2):
    nums = [int(x) for x in m.group(1).split()]
    if len(nums) == n:
        rows2.append(nums)

print(f"[*] Parsed {len(rows2)} reduced delta vectors.")
for i in range(min(5, len(rows2))):
    norm_i = float(sqrt(sum(x^2 for x in rows2[i])))
    print(f"Row {i} norm: {norm_i:.2f}, first 10: {rows2[i][:10]}")

