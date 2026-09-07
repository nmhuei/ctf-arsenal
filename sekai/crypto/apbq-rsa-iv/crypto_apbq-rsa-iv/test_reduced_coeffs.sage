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
monos = [w0^2, w1^2, w2^2, w0*w1, w0*w2, w1*w2, R(1)]
n_monos = len(monos)

raw_polys = [(ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1]
for j in range(3):
    raw_polys.append((w0*L[0, j] + w1*L[1, j] + w2*L[2, j])^2 - H[j]^2)

# Reduce all polynomials modulo n:
polys = []
for P in raw_polys:
    P_mod = sum(((P.monomial_coefficient(m) % n)) * m for m in monos)
    polys.append(P_mod)

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

all_polys = list(polys)
for m in monos[:-1]:
    all_polys.append(n * m)

M_hg = Matrix(ZZ, len(all_polys), n_monos)
for r_idx, P in enumerate(all_polys):
    for c_idx, m in enumerate(monos):
        M_hg[r_idx, c_idx] = P.monomial_coefficient(m) * col_weights[c_idx]

print(f"[*] Matrix size: {len(all_polys)}x{n_monos}. Running LLL...")
t_lll = time.time()
L_hg = M_hg.LLL()
print(f"[+] LLL completed in {time.time() - t_lll:.2f}s!")

for idx, r in enumerate(L_hg.rows()):
    if vector(r).norm() > 0:
        norm = vector(r).norm().n()
        print(f"Row {idx}: norm bits = {norm.log(2):.1f}, n bits = {n.bit_length()}")
