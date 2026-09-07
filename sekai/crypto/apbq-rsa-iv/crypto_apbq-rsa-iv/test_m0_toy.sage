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

# Cross product of w and c:
w_cross_c = vector(ZZ, [
    w[1]*c[2] - w[2]*c[1],
    w[2]*c[0] - w[0]*c[2],
    w[0]*c[1] - w[1]*c[0]
])

target = lam * z1 + mu * z2
print("w x c == lam*z1 + mu*z2:", w_cross_c == target)
if w_cross_c != target:
    print("w x c:", w_cross_c)
    print("target:", target)
    print("Ratio:", [w_cross_c[i] / target[i] for i in range(3)])

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

row0 = 2 * adjY[0]
row1 = 2 * adjY[1]

print("row0 . w == Delta_z * lam:", row0 * w == Delta_z * lam)
print("row1 . w == Delta_z * mu:", row1 * w == Delta_z * mu)
print("row0 . w / Delta_z:", (row0 * w) / Delta_z, "lam:", lam)
print("row1 . w / Delta_z:", (row1 * w) / Delta_z, "mu:", mu)

m0 = vector(QQ, [x / Delta_z for x in adjY[0]])
m1 = vector(QQ, [x / Delta_z for x in adjY[1]])

print("m0 . w == lam:", m0 * w == lam)
print("m1 . w == mu:", m1 * w == mu)

# Component k of w x c:
M_cross = Matrix(QQ, 3, 3)
M_cross[0, 0] = - (m0[0]*z1[0] + m1[0]*z2[0])
M_cross[0, 1] = c[2] - (m0[1]*z1[0] + m1[1]*z2[0])
M_cross[0, 2] = -c[1] - (m0[2]*z1[0] + m1[2]*z2[0])

M_cross[1, 0] = -c[2] - (m0[0]*z1[1] + m1[0]*z2[1])
M_cross[1, 1] = - (m0[1]*z1[1] + m1[1]*z2[1])
M_cross[1, 2] = c[0] - (m0[2]*z1[1] + m1[2]*z2[1])

M_cross[2, 0] = c[1] - (m0[0]*z1[2] + m1[0]*z2[2])
M_cross[2, 1] = -c[0] - (m0[1]*z1[2] + m1[2]*z2[2])
M_cross[2, 2] = - (m0[2]*z1[2] + m1[2]*z2[2])

print("M_cross * w == 0:", M_cross * w == vector(QQ, [0, 0, 0]))
print("M_cross * w:", M_cross * w)
