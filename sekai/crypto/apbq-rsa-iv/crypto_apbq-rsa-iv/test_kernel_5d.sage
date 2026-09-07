load('test_5d_synthetic.sage')

K_mat = Matrix(ZZ, [
    [-h[1], h[0], 0, -v1[2], -v2[2]],
    [-h[2], 0, h[0], v1[1], v2[1]],
    [0, -h[2], h[1], -v1[0], -v2[0]]
])

print("K_mat rank:", K_mat.rank())
ker_K = K_mat.right_kernel()
print("ker_K dimension:", ker_K.dimension())
print("ker_K basis:")
for v in ker_K.basis():
    print(" ", v)

true_vec = vector(ZZ, [b[0], b[1], b[2], lam_p_true, mu_p_true])
print("\ntrue_vec in ker_K?:", true_vec in ker_K)
coords = ker_K.coordinate_vector(true_vec)
print("coords in basis:", coords)

C_lam = vector(QQ, [ker_K.basis()[0][3], ker_K.basis()[1][3], ker_K.basis()[2][3]])
C_mu = vector(QQ, [ker_K.basis()[0][4], ker_K.basis()[1][4], ker_K.basis()[2][4]])

print("C_lam:", C_lam)
print("C_mu:", C_mu)

# Cross product with h:
print("C_lam x h:", C_lam.cross_product(vector(QQ, h)))
print("C_mu x h:", C_mu.cross_product(vector(QQ, h)))

# Check dot products:
print("C_lam . h:", C_lam * vector(QQ, h))
print("C_mu . h:", C_mu * vector(QQ, h))

print("C_lam . v1:", C_lam * vector(QQ, v1))
print("C_lam . v2:", C_lam * vector(QQ, v2))
print("C_mu . v1:", C_mu * vector(QQ, v1))
print("C_mu . v2:", C_mu * vector(QQ, v2))
