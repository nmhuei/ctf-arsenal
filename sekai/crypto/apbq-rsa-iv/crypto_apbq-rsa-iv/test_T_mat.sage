load('test_linear_forms_k.sage')

T_mat = Matrix(ZZ, [list(T0), list(T1), list(T2)])
print("T_mat dimensions:", T_mat.dimensions())
print("T_mat det bit length:", T_mat.det().bit_length())
print("T_mat det % n == 0:", T_mat.det() % n == 0)
print("T_mat det // (n^2):", T_mat.det() // (n^2) if T_mat.det() % (n^2) == 0 else "not div by n^2")

# Check: Kc * T_mat == H:
print("Kc * T_mat == H:", Kc * T_mat == H)
