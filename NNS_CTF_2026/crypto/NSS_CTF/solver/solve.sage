from sage.all import *
import subprocess, time, re
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

t0 = time.time()
load("/home/light/Workspace/CTF/NNS_CTF_2026/crypto/NSS_CTF/challenge/crypto_nss-ctf/output.py")

n = 256
p = 3
q = 367
R = PolynomialRing(ZZ, "x")
x = R.gen()

def center(coeffs, m):
    return [((ZZ(c) + m//2) % m) - m//2 for c in coeffs]

Pq.<xq> = GF(q)[]
Rq = Pq.quotient(xq^n + 1)
pk_poly = Rq(pk)

def get_F(idx):
    m, s = sigs[idx]
    s_cent = center(s, q)
    K_vec = [((m[i] - s_cent[i] + 1) % 3) - 1 for i in range(n)]
    return [s_cent[i] + q * K_vec[i] for i in range(n)]

# Signatures 2, 4, 9 have rejection error e == 0
F2 = get_F(2)
F4 = get_F(4)
F9 = get_F(9)

def convmat(a):
    M = []
    for i in range(n):
        row = []
        for j in range(n):
            k = (i - j) % n
            c = a[k]
            if i - j < 0:
                c = -c
            row.append(c)
        M.append(row)
    return Matrix(ZZ, M)

print("[*] Building ideal lattice...")
M = convmat(F2).stack(convmat(F4)).stack(convmat(F9))
print("[*] Computing Hermite Normal Form...")
H = M.hermite_form(include_zero_rows=False)
print(f"[*] HNF computed in {time.time() - t0:.2f}s, shape: {H.nrows()}x{H.ncols()}")

matrix_str = "[" + "\n".join("[" + " ".join(map(str, row)) + "]" for row in H) + "]"

print("[*] Running flatter...")
t1 = time.time()
res = subprocess.run(["flatter"], input=matrix_str, text=True, capture_output=True)
print(f"[*] Flatter completed in {time.time() - t1:.2f}s, returncode: {res.returncode}")

if res.returncode != 0:
    print("Flatter error:", res.stderr)
    exit(1)

out = res.stdout.strip()
rows = []
for m in re.finditer(r'\[([-\d\s]+)\]', out):
    nums = [int(x) for x in m.group(1).split()]
    if len(nums) == n:
        rows.append(nums)

print(f"[*] Parsed {len(rows)} reduced vectors.")
ct_bytes = bytes.fromhex(ct)

def rot(vec, k):
    res = [0] * n
    for i in range(n):
        idx = (i + k) % n
        sign = -1 if (i + k) >= n else 1
        res[idx] += sign * vec[i]
    return res

found = False
for r_idx, row in enumerate(rows[:20]):
    row_norm = sqrt(sum(c^2 for c in row))
    print(f"[*] Checking row {r_idx} (norm = {float(row_norm):.2f})...")
    for k in range(n):
        for sgn in [1, -1]:
            cand = [sgn * c for c in rot(row, k)]
            key = sha256(bytes(c % 256 for c in cand)).digest()
            try:
                pt = AES.new(key, AES.MODE_ECB).decrypt(ct_bytes)
                if b"NNS{" in pt:
                    flag = unpad(pt, 16).decode()
                    print("\n" + "="*50)
                    print(f"[+] FLAG FOUND: {flag}")
                    print("="*50 + "\n")
                    with open("/home/light/Workspace/CTF/NNS_CTF_2026/crypto/NSS_CTF/flag.txt", "w") as f_out:
                        f_out.write(flag + "\n")
                    found = True
                    break
            except Exception:
                pass
        if found:
            break
    if found:
        break

if not found:
    print("[-] Flag not found in tested rows.")
