load('test_Q_K_mod_MK.sage')

# In synthetic:
vec = lam_true * E1 + mu_true * E2
print('vec:', vec)

# Check dot products:
dp01 = vec * (h[1] * T0 + h[0] * T1)
dp02 = vec * (h[2] * T0 + h[0] * T2)
dp12 = vec * (h[2] * T1 + h[1] * T2)

print('dp01 % n == 0:', dp01 % n == 0)
print('dp02 % n == 0:', dp02 % n == 0)
print('dp12 % n == 0:', dp12 % n == 0)

coeff_lam_01 = E1 * (h[1] * T0 + h[0] * T1)
coeff_mu_01 = E2 * (h[1] * T0 + h[0] * T1)
print('coeff_lam_01 % n:', coeff_lam_01 % n)
print('coeff_mu_01 % n:', coeff_mu_01 % n)
