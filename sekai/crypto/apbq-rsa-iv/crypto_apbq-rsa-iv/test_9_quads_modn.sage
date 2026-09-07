load('test_T_mat.sage')

# Variables: k0, k1, k2
# Monomials: [k0, k1, k2, k0^2, k1^2, k2^2, k0*k1, k0*k2, k1*k2] (9 monomials)
# For each pair (i, j) with i, j in {0, 1, 2}:
# Eq(i, j): H[j] * (k . T[i]) - (k . T[i]) * (k . T[j]) = 0 mod n

R.<k0, k1, k2> = PolynomialRing(ZZ)
k_vec = vector(R, [k0, k1, k2])

monos = [k0, k1, k2, k0^2, k1^2, k2^2, k0*k1, k0*k2, k1*k2]

eqs = []
for i in range(3):
    for j in range(3):
        # H[j] * (k . T[i]) - (k . T[i]) * (k . T[j])
        kT_i = sum(k_vec[m] * T_mat[m, i] for m in range(3))
        kT_j = sum(k_vec[m] * T_mat[m, j] for m in range(3))
        poly = H[j] * kT_i - kT_i * kT_j
        eqs.append(poly)

# Build coefficient matrix (9 x 9):
coeff_mat = Matrix(ZZ, 9, 9)
for row_idx, poly in enumerate(eqs):
    for col_idx, m in enumerate(monos):
        coeff_mat[row_idx, col_idx] = poly.monomial_coefficient(m)

print("coeff_mat dimensions:", coeff_mat.dimensions())
print("Rank over QQ:", coeff_mat.rank())

# Rank modulo n:
M_mod = Matrix(GF(n), [[x % n for x in row] for row in coeff_mat.rows()])
print("Rank modulo n:", M_mod.rank())
