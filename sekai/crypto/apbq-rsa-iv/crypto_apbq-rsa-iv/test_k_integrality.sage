load('test_cross_Kc_W.sage')

MK = Kc * Kc
print("MK bit length:", MK.bit_length())

# For any lambda, mu:
# We need Kc x (lambda * W1 + mu * W2) to be parallel to Kc modulo MK?
# k = t * Kc + (lambda * (Kc x W1) + mu * (Kc x W2)) / MK
# For k to be in Z^3:
# lambda * (Kc x W1) + mu * (Kc x W2) must be in Z * Kc + MK * Z^3!

# Let's check the lattice of (lambda, mu) such that this holds:
# Matrix of [Kc x W1, Kc x W2, Kc, MK * I_3]:
A = Matrix(ZZ, [
    Kc_x_W1,
    Kc_x_W2,
    Kc
])
print("A dimensions:", A.dimensions())
print("det(A):", A.det())
print("det(A) == MK^2:", A.det() == MK^2)
