load('test_kernel_5d.sage')
c_vec = vector(ZZ, list(c) + [0, 0])
coords_c = ker_M.solve_left(vector(QQ, c_vec))
g_c = gcd(list(coords_c))
print("gcd of coords_c:", g_c)

c_norm_sq = c_vec * c_vec
proj_rows = []
for r in ker_M.rows():
    r_int = (c_norm_sq * r) - (r * c_vec) * c_vec
    proj_rows.append(r_int)

M_proj = Matrix(ZZ, proj_rows)
print("M_proj rank:", M_proj.rank())
g_proj = gcd(M_proj.list())
print("g_proj bit length:", g_proj.bit_length())
M_proj_prim = Matrix(ZZ, [[x // g_proj for x in row] for row in M_proj.rows()])

L_orth = Matrix(ZZ, [r for r in M_proj_prim.hermite_form().rows() if vector(r).norm() > 0]).LLL()
print("L_orth dimensions:", L_orth.dimensions())
print("L_orth row 0 norm bits:", vector(L_orth[0]).norm().n().log(2))
print("L_orth row 1 norm bits:", vector(L_orth[1]).norm().n().log(2))
print("\nL_orth Row 0:", L_orth[0])
print("\nL_orth Row 1:", L_orth[1])
