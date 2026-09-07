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

ks = [(L[i][0] * pow(int(h[0]), -1, n)) % n for i in range(3)]

R.<w0, w1, w2> = ZZ[]
monos = [w0^2, w1^2, w2^2, w0*w1, w0*w2, w1*w2, R(1)]
n_monos = len(monos)

polys = [(ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1]
for j in range(3):
    polys.append((w0*L[0, j] + w1*L[1, j] + w2*L[2, j])^2 - H[j]^2)

# Build Howgrave-Graham matrix:
# Monomial bounds:
B_w = 1 << 10
B_quad = B_w^2

col_weights = [1] * 6 + [B_quad]

all_polys = list(polys)
for m in monos[:-1]:
    all_polys.append(n * m)

M_hg = Matrix(ZZ, len(all_polys), n_monos)
for r_idx, P in enumerate(all_polys):
    for c_idx, m in enumerate(monos):
        M_hg[r_idx, c_idx] = P.monomial_coefficient(m) * col_weights[c_idx]

L_hg = M_hg.LLL()

print("LLL completed! Inspecting rows:")
for r in L_hg.rows():
    if vector(r).norm() == 0: continue
    # Reconstruct polynomial:
    P = sum((r[c_idx] // col_weights[c_idx]) * monos[c_idx] for c_idx in range(n_monos))
    val = P(w[0], w[1], w[2])
    print(f"Row norm: {vector(r).norm().n().log(2):.1f}, P(w) == 0: {val == 0}")
