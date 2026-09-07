load('test_find_w_3d.sage')
m0 = vector(ZZ, [x // Delta_z for x in row0])
m1 = vector(ZZ, [x // Delta_z for x in row1])

# w x c = (m0 . w) * z1 + (m1 . w) * z2
# Component k:
# (w x c)_k = sum_j eps(k, j, i) * w_j * c_i
# (w x c)_0 = w1*c2 - w2*c1
# (w x c)_1 = w2*c0 - w0*c2
# (w x c)_2 = w0*c1 - w1*c0

# LHS - RHS = 0:
# Row 0 (k = 0):
# w1*c2 - w2*c1 - (m0_0*w0 + m0_1*w1 + m0_2*w2)*z1_0 - (m1_0*w0 + m1_1*w1 + m1_2*w2)*z2_0 = 0
# Row 1 (k = 1):
# w2*c0 - w0*c2 - (m0 . w)*z1_1 - (m1 . w)*z2_1 = 0
# Row 2 (k = 2):
# w0*c1 - w1*c0 - (m0 . w)*z1_2 - (m1 . w)*z2_2 = 0

M_cross = Matrix(ZZ, 3, 3)

# Row 0:
M_cross[0, 0] = - (m0[0]*z1[0] + m1[0]*z2[0])
M_cross[0, 1] = c[2] - (m0[1]*z1[0] + m1[1]*z2[0])
M_cross[0, 2] = -c[1] - (m0[2]*z1[0] + m1[2]*z2[0])

# Row 1:
M_cross[1, 0] = -c[2] - (m0[0]*z1[1] + m1[0]*z2[1])
M_cross[1, 1] = - (m0[1]*z1[1] + m1[1]*z2[1])
M_cross[1, 2] = c[0] - (m0[2]*z1[1] + m1[2]*z2[1])

# Row 2:
M_cross[2, 0] = c[1] - (m0[0]*z1[2] + m1[0]*z2[2])
M_cross[2, 1] = -c[0] - (m0[1]*z1[2] + m1[1]*z2[2])
M_cross[2, 2] = - (m0[2]*z1[2] + m1[2]*z2[2])

print("M_cross shape:", M_cross.dimensions())
print("M_cross rank:", M_cross.rank())
print("M_cross kernel dimension:", M_cross.right_kernel().dimension())
ker = M_cross.right_kernel().basis_matrix()
print("Kernel basis:")
for r in ker.rows():
    print(" ", r)
