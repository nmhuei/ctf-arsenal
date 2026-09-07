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

W1 = vector(ZZ, [x // n for x in v1 * T_mat.transpose()])
W2 = vector(ZZ, [x // n for x in v2 * T_mat.transpose()])

print("W1:", W1)
print("W2:", W2)
print("W1 norm bits:", W1.norm().n().log(2))
print("W2 norm bits:", W2.norm().n().log(2))
