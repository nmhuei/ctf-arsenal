load('test_T_mat.sage')

# T0, T1, T2 are the rows of T_mat (or columns?):
# Earlier we wrote: kT_i = sum(k_vec[m] * T_mat[m, i] for m in range(3))
# So T_i is column i of T_mat!
col0 = vector(ZZ, [T_mat[m, 0] for m in range(3)])
col1 = vector(ZZ, [T_mat[m, 1] for m in range(3)])
col2 = vector(ZZ, [T_mat[m, 2] for m in range(3)])

u01 = h0 * col1 - h1 * col0
u02 = h0 * col2 - h2 * col0
u12 = h1 * col2 - h2 * col1

print("u01 % n == 0:", [x % n == 0 for x in u01])
print("u02 % n == 0:", [x % n == 0 for x in u02])
print("u12 % n == 0:", [x % n == 0 for x in u12])

print("u01 % n:", [x % n for x in u01])
print("u02 % n:", [x % n for x in u02])
print("u12 % n:", [x % n for x in u12])
