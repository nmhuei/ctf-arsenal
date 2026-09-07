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

R.<w0, w1, w2> = ZZ[]

monos = []
deg_monos = {0: [], 2: [], 4: [], 6: []}
for deg in [0, 2, 4, 6]:
    for i in range(deg, -1, -1):
        for j in range(deg - i, -1, -1):
            k = deg - i - j
            m = w0^i * w1^j * w2^k
            monos.append(m)
            deg_monos[deg].append(m)

n_monos = len(monos)

ks = [(L[i][0] * pow(int(h0), -1, n)) % n for i in range(3)]

raw_polys = [(ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1]
for j in range(3):
    raw_polys.append((w0*L[0, j] + w1*L[1, j] + w2*L[2, j])^2 - H[j]^2)

E = []
for P in raw_polys:
    E.append(sum(((P.monomial_coefficient(m) % n)) * m for m in deg_monos[2] + [R(1)]))

all_polys = []

# Group 1: E_i * E_j * E_k (mod n^3)
for i in range(4):
    for j in range(i, 4):
        for k in range(j, 4):
            all_polys.append(E[i] * E[j] * E[k])

# Group 2: n * m2 * E_i * E_j
for m in deg_monos[2]:
    for i in range(4):
        for j in range(i, 4):
            all_polys.append(n * m * E[i] * E[j])

# Group 3: n * E_i * E_j
for i in range(4):
    for j in range(i, 4):
        all_polys.append(n * E[i] * E[j])

# Group 4: n^2 * m4 * E_k
for m in deg_monos[4]:
    for k in range(4):
        all_polys.append((n^2) * m * E[k])

# Group 5: n^2 * m2 * E_k
for m in deg_monos[2]:
    for k in range(4):
        all_polys.append((n^2) * m * E[k])

# Group 6: n^2 * E_k
for k in range(4):
    all_polys.append((n^2) * E[k])

# Group 7: n^3 * m
for m in monos[:-1]:
    all_polys.append((n^3) * m)

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

# Check HNF of M_hg to get exact 50x50 lattice basis without running full LLL:
print("Computing HNF of M_hg...")
H = M_hg.hermite_form()
nz = [r for r in H.rows() if vector(r).norm() > 0]
print("HNF non-zero rows:", len(nz))
diag_entries = [nz[i][i] for i in range(len(nz))]
diag_bits = [d.bit_length() for d in diag_entries]
print("HNF diagonal bits:", diag_bits)
print("Total det bits:", sum(diag_bits))
print("Average row norm bits:", sum(diag_bits) / len(nz))
print("Target norm bits (n^3):", (n^3).bit_length())
