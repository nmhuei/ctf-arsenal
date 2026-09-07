import random
from Crypto.Util.number import getPrime

p = getPrime(60)
q = getPrime(60)
n = p * q
B = 2**18

a = [random.randint(1, B) for _ in range(3)]
b = [random.randint(1, B) for _ in range(3)]
h = [a[i]*p + b[i]*q for i in range(3)]

M = Matrix(ZZ, [
    [h[0], h[1], h[2]],
    [n,    0,    0   ],
    [0,    n,    0   ],
    [0,    0,    n   ]
])
HNF = M.hermite_form()
HNF_rows = [r for r in HNF.rows() if vector(r).norm() > 0]
L = Matrix(ZZ, HNF_rows).LLL()

H = vector(ZZ, h)
pa = vector(ZZ, [a[i]*p for i in range(3)])
c_pa = [ZZ(x) for x in L.solve_left(pa)]
x_true = c_pa[0]
y_true = c_pa[1]

print("x_true:", x_true, "y_true:", y_true)

R.<x, y> = ZZ[]
monos = [R(1), x, y, x^2, x*y, y^2]
n_monos = len(monos)

polys = []
for j in range(3):
    u = x * L[0, j] + y * L[1, j]
    F = u^2 - H[j] * u
    polys.append(F)

# Construct Howgrave-Graham matrix:
X_bound = 1 << 10
Y_bound = 1 << 10

col_weights = []
for m in monos:
    exp = m.exponents()[0]
    col_weights.append(X_bound^exp[0] * Y_bound^exp[1])

all_polys = list(polys)
for m in monos:
    all_polys.append(n * m)

M_hg = Matrix(ZZ, len(all_polys), n_monos)
for r_idx, P in enumerate(all_polys):
    for c_idx, m in enumerate(monos):
        M_hg[r_idx, c_idx] = P.monomial_coefficient(m) * col_weights[c_idx]

L_hg = M_hg.LLL()

print("LLL completed! Extracting polynomials that vanish at (x_true, y_true):")
found_polys = []
for r in L_hg.rows():
    if vector(r).norm() == 0: continue
    P = sum((r[c_idx] // col_weights[c_idx]) * monos[c_idx] for c_idx in range(n_monos))
    val = P(x_true, y_true)
    norm = vector(r).norm().n()
    print(f"Row norm: {norm.log(2):.1f}, n bits: {n.bit_length()}, P(x_true, y_true) == 0: {val == 0}")
    if val == 0 and not P.is_constant():
        found_polys.append(P)

print(f"Found {len(found_polys)} vanishing polynomials over ZZ!")
if len(found_polys) >= 2:
    res = found_polys[0].resultant(found_polys[1], y)
    roots = res.univariate_polynomial().roots(multiplicities=False)
    print("Roots for x:", roots)
    for rx in roots:
        P_y = found_polys[0](rx, y).univariate_polynomial()
        for ry in P_y.roots(multiplicities=False):
            print(f"Candidate root: ({rx}, {ry})")
            for j in range(3):
                u_cand = rx * L[0, j] + ry * L[1, j]
                g = gcd(int(u_cand), n)
                if 1 < g < n:
                    print("SUCCESS! Factored n:", g)
                    break
