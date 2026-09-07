load('test_Q_K_mod_MK.sage')
D, U, V = T_mat.smith_form()
V_inv = V.inverse()
u0 = vector(ZZ, V_inv.rows()[0])
u1 = vector(ZZ, V_inv.rows()[1])
u2 = vector(ZZ, V_inv.rows()[2])

Omega = Matrix(ZZ, [
    [u1 * v2, u2 * v2],
    [-(u1 * v1), -(u2 * v1)]
])
H0 = Omega.determinant()

Ku1 = (u0 * v1) // n
Ku2 = (u0 * v2) // n
Ku_vec = vector(ZZ, [Ku2, Ku1])

adj_Omega = Omega.adjugate()
V_prod = adj_Omega * Ku_vec

# In synthetic, compute true w1, w2:
w = vector(ZZ, [k_true * U.inverse()][0])
# Note: w0 = p*alpha0, w1 = alpha1/q, w2 = alpha2/q
w1 = w[1]
w2 = w[2]

term1 = V_prod[1] * (H0 * w1 - adj_Omega[0, 0] * lam_true + adj_Omega[0, 1] * mu_true)
term2 = V_prod[0] * (H0 * w2 - adj_Omega[1, 0] * lam_true + adj_Omega[1, 1] * mu_true)

print("term1 - term2 == 0?:", term1 - term2 == 0)
print("term1 - term2:", term1 - term2)
