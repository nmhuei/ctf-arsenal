load('test_linear_forms_k.sage')

tau0 = (T0[0] * pow(int(H[0]), -1, n)) % n
tau1 = (T1[0] * pow(int(H[0]), -1, n)) % n
tau2 = (T2[0] * pow(int(H[0]), -1, n)) % n

print("tau0 inv exists:", gcd(tau0, n) == 1)
inv_tau0 = pow(int(tau0), -1, n)

alpha1 = (tau1 * inv_tau0) % n
alpha2 = (tau2 * inv_tau0) % n

print("alpha1:", alpha1)
print("alpha2:", alpha2)

# Check Kc:
phi_c = (tau0 * Kc[0] + tau1 * Kc[1] + tau2 * Kc[2]) % n
print("phi(Kc) == 1 mod n:", phi_c == 1)

# Check that Kc satisfies k0 + alpha1*k1 + alpha2*k2 mod n:
lhs = (Kc[0] + alpha1 * Kc[1] + alpha2 * Kc[2]) % n
print("Kc[0] + alpha1*Kc[1] + alpha2*Kc[2] mod n == inv_tau0 mod n:", lhs == inv_tau0)
