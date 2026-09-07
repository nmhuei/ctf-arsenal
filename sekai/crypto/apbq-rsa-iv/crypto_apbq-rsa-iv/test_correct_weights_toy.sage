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
monos = [w0^2, w1^2, w2^2, w0*w1, w0*w2, w1*w2, R(1)]
n_monos = len(monos)

polys = [(ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1]
for j in range(3):
    polys.append((w0*L[0, j] + w1*L[1, j] + w2*L[2, j])^2 - H[j]^2)

# Correct column weights: X_k
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

L_hg = M_hg.LLL()

print("LLL completed! Inspecting rows:")
found_polys = []
for r in L_hg.rows():
    if vector(r).norm() == 0: continue
    norm = vector(r).norm().n()
    P = sum((r[c_idx] // col_weights[c_idx]) * monos[c_idx] for c_idx in range(n_monos))
    val = P(w[0], w[1], w[2])
    print(f"Row norm: {norm.log(2):.1f}, n bits: {n.bit_length()}, val == 0: {val == 0}")
    if norm.log(2) < n.bit_length():
        found_polys.append(P)

print(f"Found {len(found_polys)} polynomials with norm < n!")
if found_polys:
    R_qq.<w0, w1, w2> = QQ[]
    I = ideal([R_qq(P) for P in found_polys])
    print("Ideal dimension:", I.dimension())
    gb = I.groebner_basis()
    print("Groebner basis:")
    for g in gb:
        print(" ", g)
