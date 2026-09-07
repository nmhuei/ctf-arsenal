import time
from Crypto.Util.number import long_to_bytes

t0 = time.time()
print("[*] Loading challenge parameters...")
with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

# 1. Build public lattice Lambda in Z^3:
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

R.<x, y, z> = ZZ[]
monos = []
for deg in range(4):
    for i in range(deg, -1, -1):
        for j in range(deg - i, -1, -1):
            k = deg - i - j
            monos.append(x^i * y^j * z^k)

n_monos = len(monos)
print(f"Total monomials up to degree 3: {n_monos}")

polys = []
for j in range(3):
    u = x * L[0, j] + y * L[1, j] + z * L[2, j]
    F = u^2 - H[j] * u
    polys.append(F)
    polys.append(x * F)
    polys.append(y * F)
    polys.append(z * F)

all_polys = list(polys)
for m in monos:
    all_polys.append(n * m)

print(f"Total polynomials: {len(all_polys)}")

X_bound = 1 << 286
Y_bound = 1 << 286
Z_bound = 1 << 286

col_weights = []
for m in monos:
    exp = m.exponents()[0]
    col_weights.append(X_bound^exp[0] * Y_bound^exp[1] * Z_bound^exp[2])

M_hg = Matrix(ZZ, len(all_polys), n_monos)
for r_idx, P in enumerate(all_polys):
    for c_idx, m in enumerate(monos):
        M_hg[r_idx, c_idx] = P.monomial_coefficient(m) * col_weights[c_idx]

print(f"[*] Matrix size: {len(all_polys)}x{n_monos}. Running LLL...")
t_lll = time.time()
L_hg = M_hg.LLL()
print(f"[+] LLL completed in {time.time() - t_lll:.2f}s!")

found_polys = []
for idx, r in enumerate(L_hg.rows()):
    if vector(r).norm() == 0: continue
    norm = vector(r).norm().n()
    if norm.log(2) < n.bit_length():
        print(f"Row {idx}: norm bits = {norm.log(2):.1f} < {n.bit_length()}")
        P = sum((r[c_idx] // col_weights[c_idx]) * monos[c_idx] for c_idx in range(n_monos))
        if not P.is_constant():
            found_polys.append(P)

print(f"Found {len(found_polys)} polynomials with norm < n!")
