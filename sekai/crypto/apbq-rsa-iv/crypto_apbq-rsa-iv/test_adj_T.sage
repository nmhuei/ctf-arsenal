load('test_T_mat.sage')

adjT = T_mat.adjugate()
print("adjT % n == 0:", all(x % n == 0 for x in adjT.list()))
if all(x % n == 0 for x in adjT.list()):
    M_dual = Matrix(ZZ, [[x // n for x in row] for row in adjT.rows()])
    print("M_dual dimensions:", M_dual.dimensions())
    print("M_dual rows norm bits:", [vector(r).norm().n().log(2) for r in M_dual.rows()])
    print("M_dual det bit length:", M_dual.det().bit_length())
    print("M_dual det // n:", M_dual.det() // n if M_dual.det() % n == 0 else "not div by n")
