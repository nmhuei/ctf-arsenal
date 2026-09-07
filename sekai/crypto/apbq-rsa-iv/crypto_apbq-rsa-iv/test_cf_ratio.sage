with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h = vector(ZZ, hints)
M = Matrix(ZZ, [[hints[0], hints[1], hints[2]], [n, 0, 0], [0, n, 0], [0, 0, n]])
L = Matrix(ZZ, [r for r in M.hermite_form().rows() if vector(r).norm() > 0]).LLL()

ker_h = Matrix(ZZ, [hints]).right_kernel().basis_matrix().LLL()
v1, v2 = ker_h[0], ker_h[1]
if v1.cross_product(v2) != vector(ZZ, hints):
    if v1.cross_product(v2) == -vector(ZZ, hints):
        v2 = -v2

z1 = vector(ZZ, [x // n for x in L * v1])
z2 = vector(ZZ, [x // n for x in L * v2])
c = z1.cross_product(z2)

M_eq = Matrix(ZZ, [
    [0, -c[2], c[1], -z1[0], -z2[0]],
    [c[2], 0, -c[0], -z1[1], -z2[1]],
    [-c[1], c[0], 0, -z1[2], -z2[2]]
])
ker_M = M_eq.right_kernel().basis_matrix().LLL()
R0 = vector(ZZ, ker_M[0][:3])
R1 = vector(ZZ, ker_M[1][:3])
R2 = vector(ZZ, ker_M[2][:3])

T0 = R0 * L
T1 = R1 * L
T2 = R2 * L
T_mat = Matrix(ZZ, [list(T0), list(T1), list(T2)])

D, U, V = T_mat.smith_form()
V_inv = V.inverse()
u0 = vector(ZZ, V_inv.rows()[0])
u1 = vector(ZZ, V_inv.rows()[1])
u2 = vector(ZZ, V_inv.rows()[2])

C1 = u1.cross_product(u0)
C2 = u2.cross_product(u0)

print("C1 norm bits:", C1.norm().n().log(2))
print("C2 norm bits:", C2.norm().n().log(2))

# Check ratio C2[0] / C1[0] vs C2[1] / C1[1]:
ratio0 = QQ(C2[0]) / QQ(C1[0])
ratio1 = QQ(C2[1]) / QQ(C1[1])
ratio2 = QQ(C2[2]) / QQ(C1[2])

print("ratio0 - ratio1 bit length of diff:", (ratio0 - ratio1).abs().n().log(2))
print("ratio0 - ratio2 bit length of diff:", (ratio0 - ratio2).abs().n().log(2))
