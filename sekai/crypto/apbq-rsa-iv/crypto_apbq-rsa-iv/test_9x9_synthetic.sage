load('test_Q_K_mod_MK.sage')

# Synthetic parameters:
# k_true has size <= X_bound
X_bound = max(abs(x) for x in k_true) * 2
print("X_bound bits:", X_bound.nbits())
print("n bits:", n.nbits())

R.<k0, k1, k2> = ZZ[]
monos = [k0^2, k1^2, k2^2, k0*k1, k0*k2, k1*k2, k0, k1, k2]

# The linear forms:
tau0 = k0*T_mat[0, 0] + k1*T_mat[1, 0] + k2*T_mat[2, 0]
tau1 = k0*T_mat[0, 1] + k1*T_mat[1, 1] + k2*T_mat[2, 1]
tau2 = k0*T_mat[0, 2] + k1*T_mat[1, 2] + k2*T_mat[2, 2]

# Base 6 polynomials vanishing mod n:
P0 = tau0^2 - h[0] * tau0
P1 = tau1^2 - h[1] * tau1
P2 = tau2^2 - h[2] * tau2

P01 = tau0 * tau1 - h[1] * tau0
P02 = tau0 * tau2 - h[2] * tau0
P12 = tau1 * tau2 - h[2] * tau1

polys = [P0, P1, P2, P01, P02, P12]

# Verify they vanish mod n at k_true:
for idx, P in enumerate(polys):
    val = P(k_true[0], k_true[1], k_true[2])
    assert val % n == 0, f"Poly {idx} does not vanish mod n!"
print("[+] All 6 polynomials vanish mod n at k_true!")

# Add 9 multiples of n:
all_polys = list(polys)
for m in monos:
    all_polys.append(n * m)

# Weights:
weights = []
for m in monos:
    deg = m.total_degree()
    weights.append(X_bound^deg)

M_mat = Matrix(ZZ, len(all_polys), len(monos))
for r_idx, P in enumerate(all_polys):
    for c_idx, m in enumerate(monos):
        M_mat[r_idx, c_idx] = (P.monomial_coefficient(m) % n) * weights[c_idx]

L_red = M_mat.LLL()
print("[+] LLL done!")

nz_rows = [r for r in L_red.rows() if vector(r).norm() > 0]
print(f"Non-zero rows: {len(nz_rows)}")
for idx, r in enumerate(nz_rows[:5]):
    norm_bits = vector(r).norm().n().log(2)
    P_cand = sum((r[c_idx] // weights[c_idx]) * monos[c_idx] for c_idx in range(len(monos)))
    val = P_cand(k_true[0], k_true[1], k_true[2])
    print(f"Row {idx}: norm bits = {norm_bits:.1f}, target n bits = {n.nbits()}, P(k_true) == 0? {val == 0}")
