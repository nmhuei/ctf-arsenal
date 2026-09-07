load('test_T_mat.sage')

# Check: (h0 * T_mat.columns()[1] - h1 * T_mat.columns()[0]) % (2 * n) == 0:
col0 = vector(ZZ, [T_mat[i, 0] for i in range(3)])
col1 = vector(ZZ, [T_mat[i, 1] for i in range(3)])
col2 = vector(ZZ, [T_mat[i, 2] for i in range(3)])

diff01 = h0 * col1 - h1 * col0
diff02 = h0 * col2 - h2 * col0
diff12 = h1 * col2 - h2 * col1

print("diff01 % (2*n) == 0:", [x % (2*n) == 0 for x in diff01])
print("diff02 % (2*n) == 0:", [x % (2*n) == 0 for x in diff02])
print("diff12 % (2*n) == 0:", [x % (2*n) == 0 for x in diff12])

U01 = vector(ZZ, [x // (2*n) for x in diff01])
U02 = vector(ZZ, [x // (2*n) for x in diff02])
U12 = vector(ZZ, [x // (2*n) for x in diff12])

print("U01:", U01)
print("U02:", U02)
print("U12:", U12)
print("U01 bit lengths:", [abs(x).bit_length() for x in U01])
print("U02 bit lengths:", [abs(x).bit_length() for x in U02])
print("U12 bit lengths:", [abs(x).bit_length() for x in U12])
