load('test_Q_K_mod_MK.sage')

# h0 * Mrem1 - h1 * Mrem0 = Delta01
# Mrem0 = (-Delta01 * h1^-1) % h0
# Mrem1 = (Delta01 * h0^-1) % h1

inv_h1_mod_h0 = pow(int(h[1]), -1, h[0])
inv_h0_mod_h1 = pow(int(h[0]), -1, h[1])

phi1 = (- v1[2] * inv_h1_mod_h0) % h[0]
phi2 = (- v2[2] * inv_h1_mod_h0) % h[0]

psi1 = (v1[2] * inv_h0_mod_h1) % h[1]
psi2 = (v2[2] * inv_h0_mod_h1) % h[1]

# True values:
Delta01_true = lam_true * v1[2] + mu_true * v2[2]
Mrem0 = (-Delta01_true * inv_h1_mod_h0) % h[0]
Mrem1 = (Delta01_true * inv_h0_mod_h1) % h[1]

print("Mrem1 * h0 - Mrem0 * h1 == Delta01?:", Mrem1 * h[0] - Mrem0 * h[1] == Delta01_true)

kM0 = (lam_true * phi1 + mu_true * phi2 - Mrem0) // h[0]
kM1 = (lam_true * psi1 + mu_true * psi2 - Mrem1) // h[1]
Delta_kM = kM0 - kM1

print("True lam:", lam_true)
print("True mu:", mu_true)
print("True Delta_kM:", Delta_kM)

err = (QQ(lam_true * phi1 + mu_true * phi2) / h[0] - kM0) - (QQ(lam_true * psi1 + mu_true * psi2) / h[1] - kM1)
print("err:", err.n())
print("err log2:", err.abs().n().log(2))
print("Delta01 / (h0 * h1) log2:", (QQ(Delta01_true) / (h[0] * h[1])).abs().n().log(2))

alpha1 = QQ(phi1) / h[0] - QQ(psi1) / h[1]
alpha2 = QQ(phi2) / h[0] - QQ(psi2) / h[1]

# Construct 3x3 lattice:
# We want to find (lam, mu, Delta_kM) such that:
# |lam * alpha1 + mu * alpha2 - Delta_kM| <= err_bound
prec = (h[0] * h[1]).nbits()
S = 2^(prec)

A1 = round(S * alpha1)
A2 = round(S * alpha2)

X_bound = max(abs(lam_true), abs(mu_true)) * 4
W = 2^(X_bound.nbits())

M_lat = Matrix(ZZ, [
    [1, 0, A1],
    [0, 1, A2],
    [0, 0, S]
])

col_weights = [S // W, S // W, 1]
M_scaled = Matrix(ZZ, [
    [M_lat[r, c] * col_weights[c] for c in range(3)]
    for r in range(3)
])

L_red = M_scaled.LLL()
print("LLL done!")

for r in L_red.rows():
    unw = [r[c] // col_weights[c] for c in range(3)]
    c_lam, c_mu, c_err = unw[0], unw[1], unw[2]
    print(f"Row: lam={c_lam}, mu={c_mu}, norm={vector(r).norm().n():.2e}")
    if c_lam != 0 or c_mu != 0:
        if QQ(c_lam)/lam_true == QQ(c_mu)/mu_true:
            print("  ==> SUCCESS! Found vector proportional to (lam, mu)!")
            scale = QQ(c_lam) / lam_true
            print("  scale:", scale)
            Delta01_cand = (c_lam // scale) * v1[2] + (c_mu // scale) * v2[2]
            Mrem0_cand = (-Delta01_cand * inv_h1_mod_h0) % h[0]
            J_cand = (n * Mrem0_cand) // h[0]
            g = gcd(J_cand, n)
            print("  g == p?:", g == p)
            print("  g == q?:", g == q)
