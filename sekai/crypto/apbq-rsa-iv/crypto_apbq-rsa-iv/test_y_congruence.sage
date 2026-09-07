load('test_Q_K_mod_MK.sage')

# In synthetic instance:
# True k = k_true
# True Kc = Kc
y_true = 2 * vector(ZZ, k_true) - vector(ZZ, Kc)
print("y_true:", y_true)
print("y_true max bit length:", max(abs(x).bit_length() for x in y_true))

alpha1 = (h[1] * pow(int(h[0]), -1, n)) % n
alpha2 = (h[2] * pow(int(h[0]), -1, n)) % n

val = (y_true[0] + alpha1 * y_true[1] + alpha2 * y_true[2]) % n
print("val:", val)
print("val^2 % n == 1:", (val^2) % n == 1)
print("gcd(val - 1, n):", gcd(val - 1, n))
print("gcd(val + 1, n):", gcd(val + 1, n))
print("p:", p)
print("q:", q)
