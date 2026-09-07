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
monos = [w0^2, w1^2, w2^2, w0*w1, w0*w2, w1*w2, R(1)]

raw_polys = [(ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1]
for j in range(3):
    raw_polys.append((w0*L[0, j] + w1*L[1, j] + w2*L[2, j])^2 - H[j]^2)

polys = []
for P in raw_polys:
    polys.append(sum(((P.monomial_coefficient(m) % n)) * m for m in monos))

# Matrix in Zmod(n):
Zn = Zmod(n)
# 4 equations in [w0^2, w1^2, w2^2, w0*w1]:
# A * [w0^2, w1^2, w2^2, w0*w1]^T + B * [w0*w2, w1*w2]^T + C = 0 mod n
A = Matrix(Zn, 4, 4)
B = Matrix(Zn, 4, 2)
C_vec = vector(Zn, 4)

for i, P in enumerate(polys):
    for j in range(4):
        A[i, j] = P.monomial_coefficient(monos[j])
    B[i, 0] = P.monomial_coefficient(monos[4])
    B[i, 1] = P.monomial_coefficient(monos[5])
    C_vec[i] = P.monomial_coefficient(monos[6])

print("det(A) mod n:", A.det() != 0)
inv_A = A.inverse()

# [w0^2, w1^2, w2^2, w0*w1]^T = -inv_A * B * [w0*w2, w1*w2]^T - inv_A * C_vec
M_coeff = -inv_A * B
Const_coeff = -inv_A * C_vec

print("M_coeff shape:", M_coeff.dimensions())
print("Const_coeff shape:", len(Const_coeff))

# Equations in x, y:
# Row 0: w0^2 -> x^2
# Row 1: w1^2 -> y^2
# Row 2: w2^2 -> 1
# Row 3: w0*w1 -> x*y

alpha2, beta2 = M_coeff[2, 0], M_coeff[2, 1]
gamma2 = Const_coeff[2]

print("gamma2 == 0:", gamma2 == 0)
inv_gamma2 = Zn(1) / gamma2

R2.<x, y> = PolynomialRing(Zn)

eqs = []
# Row 0: x^2 = alpha0*x + beta0*y + (gamma0/gamma2) * (1 - alpha2*x - beta2*y)
for r_idx, lhs in [(0, x^2), (1, y^2), (3, x*y)]:
    a_r, b_r = M_coeff[r_idx, 0], M_coeff[r_idx, 1]
    g_r = Const_coeff[r_idx]
    eq = lhs - (a_r * x + b_r * y + g_r * inv_gamma2 * (1 - alpha2 * x - beta2 * y))
    eqs.append(eq)

print(f"Constructed {len(eqs)} quadratic equations in (x, y) mod n!")
for idx, eq in enumerate(eqs):
    print(f"Eq {idx}: {eq}")
