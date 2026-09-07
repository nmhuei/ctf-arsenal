load('test_Q_K_mod_MK.sage')

# In synthetic:
# lam_true, mu_true
Z_true = vector(ZZ, [lam_true^4, lam_true^3 * mu_true, lam_true^2 * mu_true^2, lam_true * mu_true^3, mu_true^4])
print("Z_true norm bits:", Z_true.norm().n().log(2))

# Compute q0, q1, q2 as quadratic forms in (lam, mu):
# Remember:
# A0 = (c00 * lam^2 + c01 * lam * mu + c02 * mu^2) mod h0
# Let's get the exact polynomials q0, q1, q2:
R.<l, m> = PolynomialRing(ZZ)

# Delta01, Delta02, Delta12:
d01 = l * v1[2] + m * v2[2]
d02 = -(l * v1[1] + m * v2[1])
d12 = l * v1[0] + m * v2[0]

inv_h1_sq_mod_h0 = pow(int(h[1]), -2, h[0])
inv_h0_sq_mod_h1 = pow(int(h[0]), -2, h[1])
inv_h0_sq_mod_h2 = pow(int(h[0]), -2, h[2])

q0_poly = (- n * inv_h1_sq_mod_h0 * d01^2)
q1_poly = (- n * inv_h0_sq_mod_h1 * d01^2)
q2_poly = (- n * inv_h0_sq_mod_h2 * d02^2)

# Check if q0(lam, mu) % h0 == A0:
A0_true = a[0] * b[0]
A1_true = a[1] * b[1]
A2_true = a[2] * b[2]

print("q0 % h0 == A0:", (q0_poly(lam_true, mu_true) - A0_true) % h[0] == 0)
print("q1 % h1 == A1:", (q1_poly(lam_true, mu_true) - A1_true) % h[1] == 0)
print("q2 % h2 == A2:", (q2_poly(lam_true, mu_true) - A2_true) % h[2] == 0)

# Now square the polynomials mod h_i^2:
sq0 = q0_poly^2
sq1 = q1_poly^2
sq2 = q2_poly^2

print("sq0 % h0^2 == A0^2:", (sq0(lam_true, mu_true) - A0_true^2) % (h[0]^2) == 0)
print("sq1 % h1^2 == A1^2:", (sq1(lam_true, mu_true) - A1_true^2) % (h[1]^2) == 0)
print("sq2 % h2^2 == A2^2:", (sq2(lam_true, mu_true) - A2_true^2) % (h[2]^2) == 0)
