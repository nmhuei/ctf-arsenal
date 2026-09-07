load('test_K_diff_gcd.sage')

# In synthetic:
# a = [a0, a1, a2], b = [b0, b1, b2]
# h = a*p + b*q
# alpha1 = h1 * h0^-1 mod n
# alpha2 = h2 * h0^-1 mod n

alpha1 = (h[1] * pow(int(h[0]), -1, n)) % n
alpha2 = (h[2] * pow(int(h[0]), -1, n)) % n

print("Target a:", a)
print("Target b:", b)
print("p:", p)
print("q:", q)

# Check:
print("a1 - alpha1 * a0 % q == 0:", (a[1] - alpha1 * a[0]) % q == 0)
print("a2 - alpha2 * a0 % q == 0:", (a[2] - alpha2 * a[0]) % q == 0)
print("b1 - alpha1 * b0 % p == 0:", (b[1] - alpha1 * b[0]) % p == 0)
print("b2 - alpha2 * b0 % p == 0:", (b[2] - alpha2 * b[0]) % p == 0)

# Monomials of degree 2:
# m = [x^2, x*y, x*z, y^2, y*z, z^2]
# Root: (a0, a1, a2)
X = 1 << B_bits
Y = 1 << B_bits
Z = 1 << B_bits

# Weights for monomials:
weights = [X^2, X*Y, X*Z, Y^2, Y*Z, Z^2]

# Polynomials vanishing mod q at a:
# 1. n * x^2
# 2. n * x * y
# 3. n * x * z
# 4. n * y^2
# 5. n * y * z
# 6. n * z^2
# 7. x * (y - alpha1 * x) = -alpha1 * x^2 + x*y
# 8. x * (z - alpha2 * x) = -alpha2 * x^2 + x*z
# 9. y * (y - alpha1 * x) = -alpha1 * x*y + y^2
# 10. z * (z - alpha2 * x) = -alpha2 * x*z + z^2
# 11. y * (z - alpha2 * x) = -alpha2 * x*y + y*z
# 12. z * (y - alpha1 * x) = -alpha1 * x*z + y*z

polys = [
    [-alpha1, 1, 0, 0, 0, 0], # x*(y - a1*x)
    [-alpha2, 0, 1, 0, 0, 0], # x*(z - a2*x)
    [0, -alpha1, 0, 1, 0, 0], # y*(y - a1*x)
    [0, 0, -alpha2, 0, 0, 1], # z*(z - a2*x)
    [0, -alpha2, 0, 0, 1, 0], # y*(z - a2*x)
    [0, 0, -alpha1, 0, 1, 0], # z*(y - a1*x)
    [n, 0, 0, 0, 0, 0],
    [0, n, 0, 0, 0, 0],
    [0, 0, n, 0, 0, 0],
    [0, 0, 0, n, 0, 0],
    [0, 0, 0, 0, n, 0],
    [0, 0, 0, 0, 0, n],
]

mat = Matrix(ZZ, [[c * w for c, w in zip(row, weights)] for row in polys])
L = mat.LLL()

print("L rows:")
for i, r in enumerate(L.rows()[:6]):
    unweighted = [r[j] // weights[j] for j in range(6)]
    # Evaluate at a:
    val_a = (unweighted[0]*a[0]^2 + unweighted[1]*a[0]*a[1] + unweighted[2]*a[0]*a[2] +
             unweighted[3]*a[1]^2 + unweighted[4]*a[1]*a[2] + unweighted[5]*a[2]^2)
    val_b = (unweighted[0]*b[0]^2 + unweighted[1]*b[0]*b[1] + unweighted[2]*b[0]*b[2] +
             unweighted[3]*b[1]^2 + unweighted[4]*b[1]*a[2] + unweighted[5]*b[2]^2)
    print(f"Row {i}: norm bits = {r.norm().n().log(2):.1f}, val_a = {val_a}, val_b = {val_b}")
