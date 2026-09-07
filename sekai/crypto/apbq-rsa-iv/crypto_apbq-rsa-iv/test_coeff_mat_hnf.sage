load('test_kernel_1d.sage')

# Augmented matrix: coeff_mat and n * I_9
# This is the lattice of relations modulo n:
M_aug = Matrix(ZZ, list(coeff_mat.rows()) + list(n * identity_matrix(ZZ, 9)))
HNF = M_aug.hermite_form()
HNF_nonzero = Matrix(ZZ, [r for r in HNF.rows() if vector(r).norm() > 0])
print("HNF dimensions:", HNF_nonzero.dimensions())
print("HNF determinant bit length:", HNF_nonzero.det().bit_length())
print("HNF det // n:", HNF_nonzero.det() // n if HNF_nonzero.det() % n == 0 else "not div by n")
print("HNF det // (n^8):", HNF_nonzero.det() // (n^8) if HNF_nonzero.det() % (n^8) == 0 else "not div by n^8")
