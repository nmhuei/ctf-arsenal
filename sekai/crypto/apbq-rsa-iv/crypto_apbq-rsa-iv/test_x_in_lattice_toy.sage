load('test_clean_50_toy.sage')

# On toy example, we have the true w = u - v.
# And true x = (w1^2, w2^2, w0*w1, w0*w2, w1*w2)
x_true = vector(ZZ, [
    w[1]^2,
    w[2]^2,
    w[0]*w[1],
    w[0]*w[2],
    w[1]*w[2]
])

print("True w:", w)
print("True x:", x_true)

# Now let's compute V5_crt on toy:
# 1. d = a x b
d = vector(ZZ, [
    a[1]*b[2] - a[2]*b[1],
    a[2]*b[0] - a[0]*b[2],
    a[0]*b[1] - a[1]*b[0]
])

M_ker = Matrix(ZZ, [list(h)]).right_kernel().basis_matrix().LLL()
v1 = M_ker[0]
v2 = M_ker[1]

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

F12 = v1[0]*m0 + v2[0]*m1
F02 = -(v1[1]*m0 + v2[1]*m1)
F01 = v1[2]*m0 + v2[2]*m1

# Check Delta_ij with true w:
print("F12 . w == d12:", abs(F12 * w) == abs(d[0]))
print("F02 . w == d02:", abs(F02 * w) == abs(-d[1]))
print("F01 . w == d01:", abs(F01 * w) == abs(d[2]))
