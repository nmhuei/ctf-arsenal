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

M_ker = Matrix(ZZ, [list(h)]).right_kernel().basis_matrix().LLL()
v1 = M_ker[0]
v2 = M_ker[1]

d = vector(ZZ, [
    a[1]*b[2] - a[2]*b[1],
    a[2]*b[0] - a[0]*b[2],
    a[0]*b[1] - a[1]*b[0]
])

lam, mu = M_ker.solve_left(d)

z1 = vector(ZZ, [ZZ(x) for x in (2 * L * v1 / n)])
z2 = vector(ZZ, [ZZ(x) for x in (2 * L * v2 / n)])

Y1 = vector(ZZ, [
    c[1]*z1[2] - c[2]*z1[1],
    c[2]*z1[0] - c[0]*z1[2],
    c[0]*z1[1] - c[1]*z1[0]
])

Y2 = vector(ZZ, [
    c[1]*z2[2] - c[2]*z2[1],
    c[2]*z2[0] - c[0]*z2[2],
    c[0]*z2[1] - c[1]*z2[0]
])

Y3 = c
Y = Matrix(ZZ, [list(Y1), list(Y2), list(Y3)]).transpose()
adjY = Y.adjugate()
Delta_z = c * vector(ZZ, [z1[1]*z2[2]-z1[2]*z2[1], z1[2]*z2[0]-z1[0]*z2[2], z1[0]*z2[1]-z1[1]*z2[0]])

m0 = vector(ZZ, [x // Delta_z for x in adjY[0]])
m1 = vector(ZZ, [x // Delta_z for x in adjY[1]])

# Check lam and mu:
print("lam check:", (m0 * w == lam) or (m0 * w == -lam))
print("mu check:", (m1 * w == mu) or (m1 * w == -mu))

# Sign check on d:
sign_lam = 1 if (m0 * w == lam) else -1
m0 *= sign_lam
m1 *= sign_lam

F12 = v1[0]*m0 + v2[0]*m1
F02 = -(v1[1]*m0 + v2[1]*m1)
F01 = v1[2]*m0 + v2[2]*m1

print("d12 check:", F12 * w == d[0])
print("d02 check:", F02 * w == -d[1])
print("d01 check:", F01 * w == d[2])

def quad_to_linear(F_A, F_B):
    return vector(ZZ, [
        F_A[0]*F_B[0],
        F_A[1]*F_B[1],
        F_A[2]*F_B[2],
        F_A[0]*F_B[1] + F_A[1]*F_B[0],
        F_A[0]*F_B[2] + F_A[2]*F_B[0],
        F_A[1]*F_B[2] + F_A[2]*F_B[1]
    ])

G0 = quad_to_linear(F01, F02)
G1 = quad_to_linear(F01, F12)
G2 = quad_to_linear(F02, F12)

x_vec = vector(ZZ, [
    w[0]^2,
    w[1]^2,
    w[2]^2,
    w[0]*w[1],
    w[0]*w[2],
    w[1]*w[2]
])

print("G0 . x == d01 * d02:", G0 * x_vec == d[2] * (-d[1]))
print("G1 . x == d01 * d12:", G1 * x_vec == d[2] * d[0])
print("G2 . x == d02 * d12:", G2 * x_vec == (-d[1]) * d[0])

L0_quad = vector(ZZ, [
    L[0, 0]^2, L[1, 0]^2, L[2, 0]^2,
    2 * L[0, 0] * L[1, 0], 2 * L[0, 0] * L[2, 0], 2 * L[1, 0] * L[2, 0]
])

L1_quad = vector(ZZ, [
    L[0, 1]^2, L[1, 1]^2, L[2, 1]^2,
    2 * L[0, 1] * L[1, 1], 2 * L[0, 1] * L[2, 1], 2 * L[1, 1] * L[2, 1]
])

L2_quad = vector(ZZ, [
    L[0, 2]^2, L[1, 2]^2, L[2, 2]^2,
    2 * L[0, 2] * L[1, 2], 2 * L[0, 2] * L[2, 2], 2 * L[1, 2] * L[2, 2]
])

inv_h1h2 = pow(int(h[1] * h[2]), -1, h[0])
coeff_G0 = (4 * n^2 * inv_h1h2) % h[0]
vec0 = vector(ZZ, [(L0_quad[i] - coeff_G0 * G0[i]) % h[0] for i in range(6)])

inv_h0h2 = pow(int(h[0] * h[2]), -1, h[1])
coeff_G1 = (4 * n^2 * inv_h0h2) % h[1]
vec1 = vector(ZZ, [(L1_quad[i] + coeff_G1 * G1[i]) % h[1] for i in range(6)])

inv_h0h1 = pow(int(h[0] * h[1]), -1, h[2])
coeff_G2 = (4 * n^2 * inv_h0h1) % h[2]
vec2 = vector(ZZ, [(L2_quad[i] - coeff_G2 * G2[i]) % h[2] for i in range(6)])

print("vec0 . x == 0 mod h0:", (vec0 * x_vec) % h[0] == 0)
print("vec1 . x == 0 mod h1:", (vec1 * x_vec) % h[1] == 0)
print("vec2 . x == 0 mod h2:", (vec2 * x_vec) % h[2] == 0)

# Lattice to find x_vec:
# x_vec in Z^6 with:
# vec0 . x = 0 mod h[0]
# vec1 . x = 0 mod h[1]
# vec2 . x = 0 mod h[2]

# Standard simultaneous Diophantine approximation / kernel lattice:
# Unknowns: x in Z^6, k0, k1, k2 in Z
# [ K * vec0[0]  K * vec1[0]  K * vec2[0]  1  0  0  0  0  0 ]
# [ K * vec0[1]  K * vec1[1]  K * vec2[1]  0  1  0  0  0  0 ]
# ...
# [ K * h[0]         0            0        0  0  0  0  0  0 ]
# [    0          K * h[1]        0        0  0  0  0  0  0 ]
# [    0             0         K * h[2]    0  0  0  0  0  0 ]

K_fac = 1 << 100
M_lat = Matrix(ZZ, 9, 9)
for i in range(6):
    M_lat[i, 0] = K_fac * vec0[i]
    M_lat[i, 1] = K_fac * vec1[i]
    M_lat[i, 2] = K_fac * vec2[i]
    M_lat[i, 3 + i] = 1

M_lat[6, 0] = K_fac * h[0]
M_lat[7, 1] = K_fac * h[1]
M_lat[8, 2] = K_fac * h[2]

L_red = M_lat.LLL()
print("LLL completed! Shortest non-zero rows:")
found = False
for r in L_red.rows():
    if vector(r).norm() > 0:
        cand_x = vector(ZZ, r[3:])
        if cand_x[0] != 0:
            print("Found row with norm:", vector(r).norm().n().log(2))
            print("cand_x:", cand_x)
            print("true x:", x_vec)
            if cand_x == x_vec or cand_x == -x_vec:
                print("[!] EXACT MATCH FOR x_vec!")
                found = True
                break
            # Check if proportional:
            if cand_x[0] * x_vec[1] == cand_x[1] * x_vec[0]:
                print("[!] Proportional match!")
                found = True
                break
