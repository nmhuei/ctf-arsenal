import time
import random
from Crypto.Util.number import getPrime

p = getPrime(60)
q = getPrime(60)
n = p * q
B = 2**18

a = vector(ZZ, [random.randint(1, B) for _ in range(3)])
b = vector(ZZ, [random.randint(1, B) for _ in range(3)])
h = a*p + b*q

M = Matrix(ZZ, [
    list(h),
    [n, 0, 0],
    [0, n, 0],
    [0, 0, n]
])
HNF = M.hermite_form()
HNF_rows = [r for r in HNF.rows() if vector(r).norm() > 0]
L = Matrix(ZZ, HNF_rows).LLL()

H = vector(ZZ, h)
pa = vector(ZZ, [a[i]*p for i in range(3)])
qb = vector(ZZ, [b[i]*q for i in range(3)])

c = vector(ZZ, [ZZ(x) for x in L.solve_left(H)])
u = vector(ZZ, [ZZ(x) for x in L.solve_left(pa)])
v = vector(ZZ, [ZZ(x) for x in L.solve_left(qb)])
w = u - v

print("True w:", w)

ks = [(L[i][0] * pow(int(h[0]), -1, n)) % n for i in range(3)]

R.<w0, w1, w2> = ZZ[]

# Even monomials up to degree 6:
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
print(f"Total monomials: {n_monos}")

# 4 Base polynomials:
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

t0 = time.time()
L_hg = M_hg.LLL()
print(f"LLL completed in {time.time() - t0:.2f}s!")

target_norm_bits = (n^3).bit_length()
print(f"Target norm bits (n^3): {target_norm_bits}")

found_polys = []
for idx, r in enumerate(L_hg.rows()):
    if vector(r).norm() == 0: continue
    norm = vector(r).norm().n()
    P = sum((r[c_idx] // col_weights[c_idx]) * monos[c_idx] for c_idx in range(n_monos))
    val = P(w[0], w[1], w[2])
    if norm.log(2) < target_norm_bits:
        found_polys.append(P)

print(f"Found {len(found_polys)} polynomials with norm < n^3!")

R_qq.<w0, w1, w2> = QQ[]
I = ideal([R_qq(P) for P in found_polys[:15]])
print(f"Ideal dimension: {I.dimension()}")
gb = I.groebner_basis()
print("Groebner basis:")
for g in gb:
    print(" ", g)
