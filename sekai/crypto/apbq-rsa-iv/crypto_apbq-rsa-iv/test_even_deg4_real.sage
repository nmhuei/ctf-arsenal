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

ks = [(L[i][0] * pow(int(h0), -1, n)) % n for i in range(3)]

R.<w0, w1, w2> = ZZ[]

# Even monomials of degree 0, 2, 4:
monos = []
for deg in [0, 2, 4]:
    for i in range(deg, -1, -1):
        for j in range(deg - i, -1, -1):
            k = deg - i - j
            monos.append(w0^i * w1^j * w2^k)

n_monos = len(monos)
print(f"Total even monomials up to degree 4: {n_monos}")

deg2_monos = [w0^2, w1^2, w2^2, w0*w1, w0*w2, w1*w2]

# Base polynomials (degree 2):
base_polys = [(ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1]
for j in range(3):
    base_polys.append((w0*L[0, j] + w1*L[1, j] + w2*L[2, j])^2 - H[j]^2)

# Shifts:
polys = list(base_polys)
for P in base_polys:
    for m in deg2_monos:
        polys.append(m * P)

all_polys = list(polys)
for m in monos[:-1]:
    all_polys.append(n * m)

print(f"Total polynomials: {len(all_polys)}")

W0 = 1 << (abs(c[0]).bit_length() + 1)
W1 = 1 << (abs(c[1]).bit_length() + 1)
W2 = 1 << (abs(c[2]).bit_length() + 1)

col_weights = []
for m in monos:
    exp = m.exponents()[0]
    col_weights.append(W0^exp[0] * W1^exp[1] * W2^exp[2])

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

print(f"[+] Found {len(found_polys)} polynomials with norm < n!")

if found_polys:
    print("[*] Step 4: Solving polynomial system over QQ...")
    R_qq.<w0, w1, w2> = QQ[]
    I = ideal([R_qq(P) for P in found_polys])
    print(f"Ideal dimension: {I.dimension()}")
    gb = I.groebner_basis()
    print(f"Groebner basis has {len(gb)} elements:")
    for g in gb:
        print(f"  {g}")
