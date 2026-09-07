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

# In Sage: D, U, V = T_mat.smith_form() such that U * T_mat * V = D
D, U, V = T_mat.smith_form()
print("D:", [D[i, i] == 1 or D[i, i] == n for i in range(3)])
print("U determinant:", U.determinant())
print("V determinant:", V.determinant())
print("U norm bits:", [vector(r).norm().n().log(2) for r in U.rows()])
print("V norm bits:", [vector(r).norm().n().log(2) for r in V.rows()])

# V columns:
V_cols = V.columns()
print("V column 1 norm bits:", vector(V_cols[1]).norm().n().log(2))
print("V column 2 norm bits:", vector(V_cols[2]).norm().n().log(2))
