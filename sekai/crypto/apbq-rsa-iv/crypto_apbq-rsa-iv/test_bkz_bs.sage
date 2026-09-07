import time
from fpylll import IntegerMatrix, BKZ, LLL

with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

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

monos = []
for deg in [0, 2, 4]:
    for i in range(deg, -1, -1):
        for j in range(deg - i, -1, -1):
            k = deg - i - j
            monos.append(w0^i * w1^j * w2^k)

n_monos = len(monos)
deg2_monos = [w0^2, w1^2, w2^2, w0*w1, w0*w2, w1*w2]

raw_polys = [(ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1]
for j in range(3):
    raw_polys.append((w0*L[0, j] + w1*L[1, j] + w2*L[2, j])^2 - H[j]^2)

E = []
for P in raw_polys:
    E.append(sum(((P.monomial_coefficient(m) % n)) * m for m in deg2_monos + [R(1)]))

all_polys = []
for i in range(4):
    for j in range(i, 4):
        all_polys.append(E[i] * E[j])
for m in deg2_monos:
    for k in range(4):
        all_polys.append(n * m * E[k])
for k in range(4):
    all_polys.append(n * E[k])
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

L_hg = M_hg.LLL()
nz = [list(r) for r in L_hg.rows() if vector(r).norm() > 0]

for bs in [8, 10, 12, 14]:
    A = IntegerMatrix.from_matrix(nz)
    t0 = time.time()
    BKZ.reduction(A, BKZ.Param(block_size=bs, max_loops=4))
    norms = [vector(ZZ, [A[i, j] for j in range(A.ncols)]).norm().n().log(2) for i in range(A.nrows)]
    print(f"BKZ-{bs} in {time.time()-t0:.2f}s: shortest = {min(norms):.1f}, target = {(n^2).bit_length()}")
