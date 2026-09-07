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

M_ker = Matrix(ZZ, [hints]).right_kernel().basis_matrix().LLL()
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

# In terms of x = (w0^2, w1^2, w2^2, w0*w1, w0*w2, w1*w2):
# Delta_01 * Delta_02 = (F01 . w) * (F02 . w)
# coeff of w_i * w_j:
def quad_to_linear(F_A, F_B):
    # F_A . w = sum_i F_A[i]*w_i
    # (F_A . w)(F_B . w) = sum_i F_A[i]*F_B[i] w_i^2 + sum_{i<j} (F_A[i]*F_B[j] + F_A[j]*F_B[i]) w_i*w_j
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

# L0^(2):
L0_quad = vector(ZZ, [
    L[0, 0]^2,
    L[1, 0]^2,
    L[2, 0]^2,
    2 * L[0, 0] * L[1, 0],
    2 * L[0, 0] * L[2, 0],
    2 * L[1, 0] * L[2, 0]
])

inv_h1h2 = pow(int(h1 * h2), -1, h0)
coeff_G0 = (4 * n^2 * inv_h1h2) % h0

vec0 = vector(ZZ, [(L0_quad[i] - coeff_G0 * G0[i]) % h0 for i in range(6)])
print("vec0 == 0 mod h0:", vec0 == vector(ZZ, [0]*6))
print("vec0:", vec0)

# L1^(2):
L1_quad = vector(ZZ, [
    L[0, 1]^2,
    L[1, 1]^2,
    L[2, 1]^2,
    2 * L[0, 1] * L[1, 1],
    2 * L[0, 1] * L[2, 1],
    2 * L[1, 1] * L[2, 1]
])

inv_h0h2 = pow(int(h0 * h2), -1, h1)
coeff_G1 = (4 * n^2 * inv_h0h2) % h1
# A1 = n (h0 h2)^-1 G1 => L1_quad . x + 4 n A1 = 0 mod h1 => L1_quad . x + 4 n^2 (h0 h2)^-1 G1 . x = 0 mod h1
vec1 = vector(ZZ, [(L1_quad[i] + coeff_G1 * G1[i]) % h1 for i in range(6)])
print("vec1 == 0 mod h1:", vec1 == vector(ZZ, [0]*6))

# L2^(2):
L2_quad = vector(ZZ, [
    L[0, 2]^2,
    L[1, 2]^2,
    L[2, 2]^2,
    2 * L[0, 2] * L[1, 2],
    2 * L[0, 2] * L[2, 2],
    2 * L[1, 2] * L[2, 2]
])

inv_h0h1 = pow(int(h0 * h1), -1, h2)
coeff_G2 = (4 * n^2 * inv_h0h1) % h2
# A2 = -n (h0 h1)^-1 G2 => L2_quad . x - 4 n^2 (h0 h1)^-1 G2 . x = 0 mod h2
vec2 = vector(ZZ, [(L2_quad[i] - coeff_G2 * G2[i]) % h2 for i in range(6)])
print("vec2 == 0 mod h2:", vec2 == vector(ZZ, [0]*6))
