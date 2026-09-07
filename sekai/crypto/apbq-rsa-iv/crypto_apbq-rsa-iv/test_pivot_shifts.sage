import time
from Crypto.Util.number import long_to_bytes

t0 = time.time()
print("[*] Loading challenge parameters...")
with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

# 1. Public lattice Lambda in Z^3:
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
monos = [w0^2, w1^2, w2^2, w0*w1, w0*w2, w1*w2, R(1)]
n_monos = len(monos)

raw_polys = [(ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1]
for j in range(3):
    raw_polys.append((w0*L[0, j] + w1*L[1, j] + w2*L[2, j])^2 - H[j]^2)

polys = []
for P in raw_polys:
    polys.append(sum(((P.monomial_coefficient(m) % n)) * m for m in monos))

# Check pivots of polys:
M_poly = Matrix(QQ, len(polys), n_monos)
for r_idx, P in enumerate(polys):
    for c_idx, m in enumerate(monos):
        M_poly[r_idx, c_idx] = P.monomial_coefficient(m)

pivots = M_poly.pivots()
print("Pivot columns of base polynomials:", pivots)
non_pivots = [c for c in range(n_monos - 1) if c not in pivots]
print("Non-pivot quadratic columns:", non_pivots)
print("Non-pivot monomials:", [monos[col_idx] for col_idx in non_pivots])

# Build minimal lattice: 4 base polys + n * non_pivot_monos:
all_polys = list(polys)
for col_idx in non_pivots:
    all_polys.append(n * monos[col_idx])

print(f"Total polynomials: {len(all_polys)} for {n_monos} monomials")

W0 = 1 << (abs(c[0]).bit_length() + 1)
W1 = 1 << (abs(c[1]).bit_length() + 1)
W2 = 1 << (abs(c[2]).bit_length() + 1)

col_weights = [
    W0^2,
    W1^2,
    W2^2,
    W0 * W1,
    W0 * W2,
    W1 * W2,
    1
]

M_hg = Matrix(ZZ, len(all_polys), n_monos)
for r_idx, P in enumerate(all_polys):
    for c_idx, m in enumerate(monos):
        M_hg[r_idx, c_idx] = P.monomial_coefficient(m) * col_weights[c_idx]

print(f"Matrix shape: {M_hg.dimensions()}, rank: {M_hg.rank()}")
print("Running LLL...")
t_lll = time.time()
L_hg = M_hg.LLL()
print(f"LLL completed in {time.time() - t_lll:.3f}s!")

target_norm_bits = n.bit_length()
print(f"Target norm bits (n): {target_norm_bits}")

found = []
for idx, r in enumerate(L_hg.rows()):
    if vector(r).norm() == 0: continue
    norm = vector(r).norm().n()
    print(f"Row {idx}: norm bits = {norm.log(2):.1f}")
    if norm.log(2) < target_norm_bits:
        P = sum((r[c_idx] // col_weights[c_idx]) * monos[c_idx] for c_idx in range(n_monos))
        if not P.is_constant():
            found.append((norm.log(2), P))

print(f"[+] Found {len(found)} non-constant polynomials with norm < n!")
