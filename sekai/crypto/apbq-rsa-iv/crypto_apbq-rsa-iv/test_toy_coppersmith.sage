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

print("x_true:", x_true)
print("y_true:", y_true)

# True target vector:
X_true = x_true^2
Y_true = x_true * y_true
Z_true = y_true^2

# Matrix of equations:
# For each j: a_x*x + a_y*y + a_X*X + a_Y*Y + a_Z*Z = 0 mod n
# Let's verify this holds:
eqs = []
for j in range(3):
    L0j = L[0, j]
    L1j = L[1, j]
    Hj = H[j]

    a_x = (-Hj * L0j) % n
    a_y = (-Hj * L1j) % n
    a_X = (L0j^2) % n
    a_Y = (2 * L0j * L1j) % n
    a_Z = (L1j^2) % n

    val = (a_x * x_true + a_y * y_true + a_X * X_true + a_Y * Y_true + a_Z * Z_true) % n
    assert val == 0
    eqs.append((a_x, a_y, a_X, a_Y, a_Z))

print("All 3 modular equations hold exactly!")

# Now construct lattice:
# Variables: x, y, X, Y, Z
# Target vector has size:
# x, y ~ B_lin
# X, Y, Z ~ B_quad = B_lin^2
# Scale x, y by B_lin so x * B_lin ~ B_quad!
# Matrix:
# [ B_lin * K, 0, 0, 0, 0, a_{0,x}*K, a_{1,x}*K, a_{2,x}*K ]
# [ 0, B_lin * K, 0, 0, 0, a_{0,y}*K, a_{1,y}*K, a_{2,y}*K ]
# [ 0, 0, K, 0, 0, a_{0,X}*K, a_{1,X}*K, a_{2,X}*K ]
# [ 0, 0, 0, K, 0, a_{0,Y}*K, a_{1,Y}*K, a_{2,Y}*K ]
# [ 0, 0, 0, 0, K, a_{0,Z}*K, a_{1,Z}*K, a_{2,Z}*K ]
# [ 0, 0, 0, 0, 0, n * K, 0, 0 ]
# [ 0, 0, 0, 0, 0, 0, n * K, 0 ]
# [ 0, 0, 0, 0, 0, 0, 0, n * K ]

B_lin = 1 << 10
B_quad = 1 << 20
K = 1 # or larger

M_lat = Matrix(ZZ, 8, 8)
M_lat[0, 0] = B_lin
M_lat[1, 1] = B_lin
M_lat[2, 2] = 1
M_lat[3, 3] = 1
M_lat[4, 4] = 1

# Large weight W on the relation columns:
W = 1 << 60
for j in range(3):
    M_lat[0, 5 + j] = eqs[j][0] * W
    M_lat[1, 5 + j] = eqs[j][1] * W
    M_lat[2, 5 + j] = eqs[j][2] * W
    M_lat[3, 5 + j] = eqs[j][3] * W
    M_lat[4, 5 + j] = eqs[j][4] * W
    M_lat[5 + j, 5 + j] = n * W

L_res = M_lat.LLL()

print("Checking L_res rows:")
for r in L_res.rows():
    if vector(r).norm() == 0: continue
    # Extract candidate x, y:
    cand_x = r[0] // B_lin
    cand_y = r[1] // B_lin
    if cand_x == 0 and cand_y == 0: continue
    # Test if cand_x, cand_y factors n:
    for j in range(3):
        u_cand = cand_x * L[0, j] + cand_y * L[1, j]
        g = gcd(int(u_cand), n)
        if 1 < g < n:
            print(f"FOUND FACTOR OF N! g = {g}")
            print(f"g == p: {g == p}, g == q: {g == q}")
            break
