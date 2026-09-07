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

# Monomials of degree 1, 2, 3:
R.<x, y> = ZZ[]
monos = [x, y, x^2, x*y, y^2, x^3, x^2*y, x*y^2, y^3]
n_monos = len(monos)

polys = []
for j in range(3):
    u = x * L[0, j] + y * L[1, j]
    F = u^2 - H[j] * u
    polys.append(F)
    polys.append(x * F)
    polys.append(y * F)

print(f"Total polys: {len(polys)}, total monos: {n_monos}")
# Check that all polys evaluate to 0 mod n at (x_true, y_true):
for idx, poly in enumerate(polys):
    val = poly(x_true, y_true)
    assert val % n == 0

print("All 9 polynomials vanish mod n!")

# Construct lattice:
B_lin = 1 << 10
weights = [
    B_lin^2, B_lin^2,
    B_lin, B_lin, B_lin,
    1, 1, 1, 1
]

W = 1 << 60
M_lat = Matrix(ZZ, n_monos + len(polys), n_monos + len(polys))
for i in range(n_monos):
    M_lat[i, i] = weights[i]

for i in range(len(polys)):
    for j in range(n_monos):
        coeff = polys[i].monomial_coefficient(monos[j]) % n
        M_lat[j, n_monos + i] = coeff * W
    M_lat[n_monos + i, n_monos + i] = n * W

L_res = M_lat.LLL()

print("Checking L_res:")
for r in L_res.rows():
    if vector(r).norm() == 0: continue
    cand_x = r[0] // weights[0]
    cand_y = r[1] // weights[1]
    if cand_x == 0 and cand_y == 0: continue
    print("Found non-zero candidate:", cand_x, cand_y)
    for j in range(3):
        u_cand = cand_x * L[0, j] + cand_y * L[1, j]
        g = gcd(int(u_cand), n)
        if 1 < g < n:
            print("SUCCESS! Factored n:", g)
            print("g == p:", g == p, "g == q:", g == q)
            break
    break
