load('test_k_integrality.sage')

col0 = vector(ZZ, [T_mat[m, 0] for m in range(3)])
col1 = vector(ZZ, [T_mat[m, 1] for m in range(3)])
col2 = vector(ZZ, [T_mat[m, 2] for m in range(3)])

F1_0 = Kc_x_W1 * col0
F2_0 = Kc_x_W2 * col0

F1_1 = Kc_x_W1 * col1
F2_1 = Kc_x_W2 * col1

F1_2 = Kc_x_W1 * col2
F2_2 = Kc_x_W2 * col2

print("F1_0 bit length:", abs(F1_0).bit_length())
print("F2_0 bit length:", abs(F2_0).bit_length())

# Check: (F1_0 * h1 - F1_1 * h0) / MK:
print("(F1_1 * h0 - F1_0 * h1) % MK == 0:", (F1_1 * h0 - F1_0 * h1) % MK == 0)
print("(F2_1 * h0 - F2_0 * h1) % MK == 0:", (F2_1 * h0 - F2_0 * h1) % MK == 0)

# Check mod n:
print("F1_0 % n == 0:", F1_0 % n == 0)
print("F2_0 % n == 0:", F2_0 % n == 0)
