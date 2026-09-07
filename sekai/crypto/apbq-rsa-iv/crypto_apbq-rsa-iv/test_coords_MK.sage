load('test_Q_K_mod_MK.sage')

# Check coordinate 1 and 2:
# Kdot * Kc[1] = - (lam * E1[1] + mu * E2[1]) mod MK
# Kdot * Kc[2] = - (lam * E1[2] + mu * E2[2]) mod MK
for j in range(3):
    val = (Kdot * Kc[j] + lam_true * E1[j] + mu_true * E2[j]) % MK
    print(f'Coord {j} % MK == 0:', val == 0)

# What about the relation between Coord 0 and Coord 1:
# Kc[1] * (lam * E1[0] + mu * E2[0]) - Kc[0] * (lam * E1[1] + mu * E2[1]) = 0 mod MK?
cross_E = Kc[1] * (lam_true * E1[0] + mu_true * E2[0]) - Kc[0] * (lam_true * E1[1] + mu_true * E2[1])
print('cross_E % MK == 0:', cross_E % MK == 0)
print('cross_E == 0:', cross_E == 0)
