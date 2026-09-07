with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

M = Matrix(ZZ, [[hints[0], hints[1], hints[2]], [n, 0, 0], [0, n, 0], [0, 0, n]])
L = Matrix(ZZ, [r for r in M.hermite_form().rows() if vector(r).norm() > 0]).LLL()

# Ker of hints:
ker_h = Matrix(ZZ, [hints]).right_kernel().basis_matrix().LLL()
v1, v2 = ker_h[0], ker_h[1]

# z1, z2:
z1 = vector(ZZ, [x // n for x in L * v1])
z2 = vector(ZZ, [x // n for x in L * v2])
c = z1.cross_product(z2)

# Dual basis for orthogonal to c:
# Or ker_M:
M_eq = Matrix(ZZ, [
    [0, -c[2], c[1], -z1[0], -z2[0]],
    [c[2], 0, -c[0], -z1[1], -z2[1]],
    [-c[1], c[0], 0, -z1[2], -z2[2]]
])
ker_M = M_eq.right_kernel().basis_matrix().LLL()
R0 = vector(ZZ, ker_M[0][:3])
R1 = vector(ZZ, ker_M[1][:3])
R2 = vector(ZZ, ker_M[2][:3])

c_vec = vector(ZZ, list(c) + [0, 0])
coords_c = ker_M.solve_left(vector(QQ, c_vec))
Kc = vector(ZZ, coords_c)

T0 = R0 * L
T1 = R1 * L
T2 = R2 * L

T_mat = Matrix(ZZ, [list(T0), list(T1), list(T2)])
print("Kc:", Kc)
print("Kc bit lengths:", [abs(x).bit_length() for x in Kc])
print("T_mat row bit lengths:", [[abs(x).bit_length() for x in row] for row in T_mat.rows()])
print("Kc * T_mat == hints:", Kc * T_mat == vector(ZZ, hints))
