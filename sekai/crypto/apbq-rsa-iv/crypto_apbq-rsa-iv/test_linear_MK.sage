load('test_Q_K_mod_MK.sage')

coeff_lam = (Kc[1] * E1[0] - Kc[0] * E1[1]) % MK
coeff_mu = (Kc[1] * E2[0] - Kc[0] * E2[1]) % MK

print('coeff_lam:', coeff_lam)
print('coeff_mu:', coeff_mu)
print('gcd(coeff_lam, MK):', gcd(coeff_lam, MK))
print('gcd(coeff_mu, MK):', gcd(coeff_mu, MK))

val = (coeff_lam * lam_true + coeff_mu * mu_true) % MK
print('linear relation mod MK == 0:', val == 0)
