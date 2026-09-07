import time
from Crypto.Util.number import long_to_bytes

t0 = time.time()
with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

# 1. Build lattice Lambda = < H, n*e0, n*e1, n*e2 >
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
print(f"Computed c in {time.time() - t0:.2f}s: {c}")
print(f"c bit lengths: {[abs(x).bit_length() for x in c]}")

# 2. Setup the 3 quadratic equations in (x, y):
# For j in {0, 1, 2}:
# (x*L[0,j] + y*L[1,j])^2 - H[j]*(x*L[0,j] + y*L[1,j]) = 0 mod n
# Variables: X=x^2, Y=x*y, Z=y^2, x, y
# Max bounds: X_bound = 2^572, x_bound = 2^286
B_quad = 1 << 572
B_lin = 1 << 286

# Weights to balance the coordinates:
# Target vector is (x, y, X, Y, Z, ...)
# Let's use a standard CVP / kernel lattice:
# Matrix rows:
# [ B_lin, 0, 0, 0, 0, a_{0,x}, a_{1,x}, a_{2,x} ]
# [ 0, B_lin, 0, 0, 0, a_{0,y}, a_{1,y}, a_{2,y} ]
# [ 0, 0, B_quad, 0, 0, a_{0,X}, a_{1,X}, a_{2,X} ]
# [ 0, 0, 0, B_quad, 0, a_{0,Y}, a_{1,Y}, a_{2,Y} ]
# [ 0, 0, 0, 0, B_quad, a_{0,Z}, a_{1,Z}, a_{2,Z} ]
# [ 0, 0, 0, 0, 0, n, 0, 0 ]
# [ 0, 0, 0, 0, 0, 0, n, 0 ]
# [ 0, 0, 0, 0, 0, 0, 0, n ]

M_lin = Matrix(ZZ, 8, 8)
# Scale factor for the relation columns:
K = B_quad

for j in range(3):
    L0j = L[0, j]
    L1j = L[1, j]
    Hj = H[j]

    a_x = (-Hj * L0j) % n
    a_y = (-Hj * L1j) % n
    a_X = (L0j^2) % n
    a_Y = (2 * L0j * L1j) % n
    a_Z = (L1j^2) % n

    M_lin[0, 5 + j] = (a_x * K) % (n * K) # wait, just (a_x * K)
    M_lin[1, 5 + j] = (a_y * K) % (n * K)
    M_lin[2, 5 + j] = (a_X * K) % (n * K)
    M_lin[3, 5 + j] = (a_Y * K) % (n * K)
    M_lin[4, 5 + j] = (a_Z * K) % (n * K)
    M_lin[5 + j, 5 + j] = n * K

M_lin[0, 0] = B_quad // B_lin * B_quad # wait, let's normalize so all coordinates have same scale!
