load('test_kernel_5d.sage')

# Delta01, Delta02, Delta12 are known in synthetic:
print("Delta01:", Delta01)
print("Delta02:", Delta02)
print("Delta12:", Delta12)

inv_H1_mod_H0 = pow(int(h[1]), -1, h[0])
M_rem_0 = (Delta01 * inv_H1_mod_H0) % h[0]
print("M_rem_0:", M_rem_0)

# Compute candidate J:
J_cand1 = (n * M_rem_0) // h[0]
J_cand2 = J_cand1 + 1

print("Testing J_cand1...")
g1 = gcd(J_cand1, n)
print("gcd(J_cand1, n):", g1, "== p?:", g1 == p or g1 == q)

print("Testing J_cand2...")
g2 = gcd(J_cand2, n)
print("gcd(J_cand2, n):", g2, "== p?:", g2 == p or g2 == q)

# Also check gcd(J - 1, n):
print("gcd(J_cand1 - 1, n):", gcd(J_cand1 - 1, n))
print("gcd(J_cand2 - 1, n):", gcd(J_cand2 - 1, n))
