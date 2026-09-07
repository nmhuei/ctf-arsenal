load('test_Q_K_mod_MK.sage')

X_bound = max(abs(x) for x in k_true) * 2

R.<k0, k1, k2> = ZZ[]
monos = [k0^2, k1^2, k2^2, k0*k1, k0*k2, k1*k2, k0, k1, k2]

tau0 = k0*T_mat[0, 0] + k1*T_mat[1, 0] + k2*T_mat[2, 0]
tau1 = k0*T_mat[0, 1] + k1*T_mat[1, 1] + k2*T_mat[2, 1]
tau2 = k0*T_mat[0, 2] + k1*T_mat[1, 2] + k2*T_mat[2, 2]

P0 = tau0^2 - h[0] * tau0
P1 = tau1^2 - h[1] * tau1
P2 = tau2^2 - h[2] * tau2

P01 = tau0 * tau1 - h[1] * tau0
P02 = tau0 * tau2 - h[2] * tau0
P12 = tau1 * tau2 - h[2] * tau1

polys = [P0, P1, P2, P01, P02, P12]

# Add 9 multiples of n:
# Modulus is n:
weights = [X_bound^m.total_degree() for m in monos]

M_mat = Matrix(ZZ, len(polys) + len(monos), len(monos))
for r_idx, P in enumerate(polys):
    for c_idx, m in enumerate(monos):
        M_mat[r_idx, c_idx] = (P.monomial_coefficient(m) % n) * weights[c_idx]

for r_idx, m_diag in enumerate(monos):
    M_mat[len(polys) + r_idx, r_idx] = n * weights[r_idx]

L_red = M_mat.LLL()
print("[+] LLL done!")

nz_rows = [r for r in L_red.rows() if vector(r).norm() > 0]
print(f"Non-zero rows: {len(nz_rows)}")
for idx, r in enumerate(nz_rows[:9]):
    norm_bits = vector(r).norm().n().log(2)
    P_cand = sum((r[c_idx] // weights[c_idx]) * monos[c_idx] for c_idx in range(len(monos)))
    val = P_cand(k_true[0], k_true[1], k_true[2])
    print(f"Row {idx}: norm bits = {norm_bits:.1f}, target n bits = {n.nbits()}, P(k_true) == 0? {val == 0}")
