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
u0 = vector(QQ, V_inv.rows()[0])
u1 = vector(QQ, V_inv.rows()[1])
u2 = vector(QQ, V_inv.rows()[2])

# Projection onto orthogonal complement of u0:
# u_perp = u - (u . u0 / |u0|^2) u0
u0_norm_sq = u0 * u0
u1_perp = u1 - (u1 * u0 / u0_norm_sq) * u0
u2_perp = u2 - (u2 * u0 / u0_norm_sq) * u0

print("u1_perp norm:", u1_perp.norm().n())
print("u2_perp norm:", u2_perp.norm().n())

# Angle between u1_perp and u2_perp:
cos_theta = (u1_perp * u2_perp) / (u1_perp.norm() * u2_perp.norm())
print("cos(theta):", cos_theta.n())
print("1 - cos^2(theta):", (1 - cos_theta^2).n())

# Ratio:
ratio = - (u1_perp * u2_perp) / (u1_perp * u1_perp)
print("ratio:", ratio.n())
