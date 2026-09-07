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

sign_lam = 1 if (m0 * w == lam) else -1
m0 *= sign_lam
m1 *= sign_lam

F12 = v1[0]*m0 + v2[0]*m1
F02 = -(v1[1]*m0 + v2[1]*m1)
F01 = v1[2]*m0 + v2[2]*m1

# C(w) = H[1]*H[2]*(F12 . w)*(H[0]^2 - (w . L)_0^2) - H[0]*H[2]*(F02 . w)*(H[1]^2 - (w . L)_1^2) + H[0]*H[1]*(F01 . w)*(H[2]^2 - (w . L)_2^2) + 4*n^2*(F01 . w)*(F02 . w)*(F12 . w)

w_dot_L = w * L
term0 = H[1]*H[2]*(F12 * w)*(H[0]^2 - w_dot_L[0]^2)
term1 = - H[0]*H[2]*(F02 * w)*(H[1]^2 - w_dot_L[1]^2)
term2 = H[0]*H[1]*(F01 * w)*(H[2]^2 - w_dot_L[2]^2)
term3 = 4 * n^2 * (F01 * w) * (F02 * w) * (F12 * w)

val = term0 + term1 + term2 + term3
print("C(w) == 0:", val == 0)
if val != 0:
    print("val:", val)
