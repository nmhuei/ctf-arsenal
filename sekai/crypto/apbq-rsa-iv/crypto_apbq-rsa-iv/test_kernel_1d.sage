load('test_T_mat.sage')

R.<k0, k1, k2> = PolynomialRing(ZZ)
k_vec = vector(R, [k0, k1, k2])
monos = [k0, k1, k2, k0^2, k1^2, k2^2, k0*k1, k0*k2, k1*k2]

eqs = []
for i in range(3):
    for j in range(3):
        kT_i = sum(k_vec[m] * T_mat[m, i] for m in range(3))
        kT_j = sum(k_vec[m] * T_mat[m, j] for m in range(3))
        poly = H[j] * kT_i - kT_i * kT_j
        eqs.append(poly)

coeff_mat = Matrix(ZZ, 9, 9)
for row_idx, poly in enumerate(eqs):
    for col_idx, m in enumerate(monos):
        coeff_mat[row_idx, col_idx] = poly.monomial_coefficient(m)

print("Rank over QQ:", coeff_mat.rank())
ker_Q = coeff_mat.right_kernel()
print("ker_Q basis:")
for v in ker_Q.basis():
    print(v)

# Check Kc evaluation on monos:
Kc_monos = vector(QQ, [
    Kc[0], Kc[1], Kc[2],
    Kc[0]^2, Kc[1]^2, Kc[2]^2,
    Kc[0]*Kc[1], Kc[0]*Kc[2], Kc[1]*Kc[2]
])

print("coeff_mat * Kc_monos == 0:", coeff_mat * Kc_monos == 0)
