load('test_Q_K_mod_MK.sage')

print("True lam, mu:", lam_true, mu_true)
print("True rho = lam/mu mod MK:")
try:
    inv_mu = pow(int(mu_true), -1, MK)
    rho_true = (lam_true * inv_mu) % MK
    print("  rho_true:", rho_true)
except Exception as e:
    print("mu_true not invertible:", e)
    inv_lam = pow(int(lam_true), -1, MK)
    rho_true = None

print("Coeffs of Q_K:")
print("  coeff_lam2:", coeff_lam2)
print("  coeff_lam_mu:", coeff_lam_mu)
print("  coeff_mu2:", coeff_mu2)

# Check if Q_K(rho, 1) % MK == 0:
if rho_true is not None:
    val = (coeff_lam2 * rho_true^2 + coeff_lam_mu * rho_true + coeff_mu2) % MK
    print("Q_K(rho_true, 1) % MK == 0:", val == 0)

# Solve Q_K(x, 1) = 0 mod MK using Sage:
R = Integers(MK)
Rx.<x> = PolynomialRing(R)
poly = coeff_lam2 * x^2 + coeff_lam_mu * x + coeff_mu2
print("Roots of poly mod MK:")
try:
    rts = poly.roots()
    print("  Found roots:", len(rts))
    for r, mult in rts:
        print("    r =", r, "matches rho_true?:", r == rho_true)
except Exception as e:
    print("Error finding roots:", e)
