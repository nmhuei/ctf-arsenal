import time
from Crypto.Util.number import long_to_bytes

t_start = time.time()
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

# Even monomials up to degree 4:
monos = []
deg_monos = {0: [], 2: [], 4: []}
for deg in [0, 2, 4]:
    for i in range(deg, -1, -1):
        for j in range(deg - i, -1, -1):
            k = deg - i - j
            m = w0^i * w1^j * w2^k
            monos.append(m)
            deg_monos[deg].append(m)

n_monos = len(monos)

raw_polys = [(ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1]
for j in range(3):
    raw_polys.append((w0*L[0, j] + w1*L[1, j] + w2*L[2, j])^2 - H[j]^2)

E = []
for P in raw_polys:
    E.append(sum(((P.monomial_coefficient(m) % n)) * m for m in deg_monos[2] + [R(1)]))

all_polys = []

# Group 1: E_i * E_j
for i in range(4):
    for j in range(i, 4):
        all_polys.append(E[i] * E[j])

# Group 2: n * m2 * E_k
for m in deg_monos[2]:
    for k in range(4):
        all_polys.append(n * m * E[k])

# Group 3: n * E_k
for k in range(4):
    all_polys.append(n * E[k])

# Group 4: n^2 * m
for m in monos[:-1]:
    all_polys.append((n^2) * m)

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

print(f"Matrix shape: {M_hg.dimensions()}")
print("Running LLL first...")
t0 = time.time()
L_hg = M_hg.LLL()
print(f"LLL completed in {time.time() - t0:.2f}s!")

# Keep only non-zero rows from LLL (at most 22 rows):
nz_rows = [r for r in L_hg.rows() if vector(r).norm() > 0]
M_22 = Matrix(ZZ, nz_rows)
print(f"Non-zero rows: {len(nz_rows)}")

target_norm_bits = (n^2).bit_length()
print(f"Target norm bits (n^2): {target_norm_bits}")

print("Running BKZ with block_size=15...")
t_bkz = time.time()
L_bkz = M_22.BKZ(block_size=15)
print(f"BKZ completed in {time.time() - t_bkz:.2f}s!")

for idx, r in enumerate(L_bkz.rows()):
    norm = vector(r).norm().n()
    print(f"Row {idx}: norm bits = {norm.log(2):.1f}")
