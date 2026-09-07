load('test_Q_K_mod_MK.sage')

# In synthetic:
A0 = a[0] * b[0]
A1 = a[1] * b[1]
A2 = a[2] * b[2]

Delta01 = a[0]*b[1] - a[1]*b[0]

K_diff = (A0 * h[1]^2 - A1 * h[0]^2) // Delta01
print('K_diff is exact integer?:', (A0 * h[1]^2 - A1 * h[0]^2) % Delta01 == 0)

# Check K_diff^2 - h0^2 * h1^2 % n == 0:
prod_h = h[0] * h[1]
print('K_diff^2 - prod_h^2 % n == 0:', (K_diff^2 - prod_h^2) % n == 0)

# Check GCDs:
g1 = gcd(K_diff - prod_h, n)
g2 = gcd(K_diff + prod_h, n)

print('gcd(K_diff - prod_h, n):', g1, '== p?:', g1 == p or g1 == q)
print('gcd(K_diff + prod_h, n):', g2, '== p?:', g2 == p or g2 == q)
