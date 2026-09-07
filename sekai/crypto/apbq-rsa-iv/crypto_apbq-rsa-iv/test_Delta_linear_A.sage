load('test_K_diff_gcd.sage')

alpha1 = (h[1] * pow(int(h[0]), -1, n)) % n
alpha2 = (h[2] * pow(int(h[0]), -1, n)) % n
alpha12 = (h[2] * pow(int(h[1]), -1, n)) % n

inv_alpha1 = pow(int(alpha1), -1, n)
inv_alpha2 = pow(int(alpha2), -1, n)
inv_alpha12 = pow(int(alpha12), -1, n)

val1 = (alpha1 * A0 - inv_alpha1 * A1) % n
val2 = (alpha2 * A0 - inv_alpha2 * A2) % n
val12 = (alpha12 * A1 - inv_alpha12 * A2) % n

print('Delta01 % n == val1:', (Delta01 - val1) % n == 0)
print('Delta01 % n == -val1:', (Delta01 + val1) % n == 0)

print('Delta02 % n == val2:', (Delta02 - val2) % n == 0)
print('Delta02 % n == -val2:', (Delta02 + val2) % n == 0)

print('Delta12 % n == val12:', (Delta12 - val12) % n == 0)
print('Delta12 % n == -val12:', (Delta12 + val12) % n == 0)
