load('test_adj_T.sage')

h_vec = vector(ZZ, hints)
h_Mdual = h_vec * M_dual
print("h * M_dual % n == 0:", [x % n == 0 for x in h_Mdual])
print("(h * M_dual) // n == Kc:", vector(ZZ, [x // n for x in h_Mdual]) == Kc)
