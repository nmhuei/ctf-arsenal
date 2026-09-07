import time
from Crypto.Util.number import long_to_bytes

t0 = time.time()
print("[*] Loading challenge parameters...")
with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

# 1. Build public lattice Lambda in Z^3:
print("[*] Step 1: Building public lattice Lambda in Z^3...")
M = Matrix(ZZ, [
    [h0, h1, h2],
    [n,  0,  0 ],
    [0,  n,  0 ],
    [0,  0,  n ]
])
HNF = M.hermite_form()
HNF_rows = [r for r in HNF.rows() if vector(r).norm() > 0]
L = Matrix(ZZ, HNF_rows).LLL()

H = vector(ZZ, [h0, h1, h2])
c = vector(ZZ, [ZZ(x) for x in L.solve_left(H)])
print(f"[+] Lattice reduced! c = {c}")
print(f"c bit lengths: {[abs(x).bit_length() for x in c]}")

R.<x, y> = ZZ[]
monos = [R(1), x, y, x^2, x*y, y^2]
n_monos = len(monos)

polys = []
for j in range(3):
    u = x * L[0, j] + y * L[1, j]
    F = u^2 - H[j] * u
    polys.append(F)

# Construct Howgrave-Graham matrix:
X_bound = 1 << 286
Y_bound = 1 << 286

col_weights = []
for m in monos:
    exp = m.exponents()[0]
    col_weights.append(X_bound^exp[0] * Y_bound^exp[1])

all_polys = list(polys)
for m in monos:
    all_polys.append(n * m)

M_hg = Matrix(ZZ, len(all_polys), n_monos)
for r_idx, P in enumerate(all_polys):
    for c_idx, m in enumerate(monos):
        M_hg[r_idx, c_idx] = P.monomial_coefficient(m) * col_weights[c_idx]

print("[*] Running LLL on Howgrave-Graham matrix...")
L_hg = M_hg.LLL()

print(f"[+] LLL completed in {time.time() - t0:.2f}s!")
for idx, r in enumerate(L_hg.rows()):
    if vector(r).norm() > 0:
        norm = vector(r).norm().n()
        print(f"Row {idx}: norm bits = {norm.log(2):.1f}, n bits = {n.bit_length()}")
