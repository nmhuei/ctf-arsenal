load('test_K_diff_gcd.sage')

alpha1 = (h[1] * pow(int(h[0]), -1, n)) % n
alpha2 = (h[2] * pow(int(h[0]), -1, n)) % n

X = 1 << B_bits
Y = 1 << B_bits
Z = 1 << B_bits
weights = [X^2, X*Y, X*Z, Y^2, Y*Z, Z^2]

# The 6 polynomials divisible by q^2 at a (and p^2 at b):
# Monomials: x^2, x*y, x*z, y^2, y*z, z^2
# 1. n^2 * x^2
# 2. n * x * (y - alpha1 * x) = -alpha1 * n * x^2 + n * x*y
# 3. n * x * (z - alpha2 * x) = -alpha2 * n * x^2 + n * x*z
# 4. (y - alpha1 * x)^2 = alpha1^2 * x^2 - 2*alpha1 * x*y + y^2
# 5. (y - alpha1 * x)*(z - alpha2 * x) = alpha1*alpha2 * x^2 - alpha2 * x*y - alpha1 * x*z + y*z
# 6. (z - alpha2 * x)^2 = alpha2^2 * x^2 - 2*alpha2 * x*z + z^2

polys = [
    [n^2, 0, 0, 0, 0, 0],
    [-alpha1 * n, n, 0, 0, 0, 0],
    [-alpha2 * n, 0, n, 0, 0, 0],
    [alpha1^2, -2*alpha1, 0, 1, 0, 0],
    [alpha1*alpha2, -alpha2, -alpha1, 0, 1, 0],
    [alpha2^2, 0, -2*alpha2, 0, 0, 1],
]

mat = Matrix(ZZ, [[c * w for c, w in zip(row, weights)] for row in polys])
print("Matrix determinant bit length:", mat.determinant().abs().n().log(2))
print("Target q^2 bit length:", (q^2).bit_length())
print("Target p^2 bit length:", (p^2).bit_length())

L = mat.LLL()
print("LLL shortest vector norm bits:", vector(L[0]).norm().n().log(2))

for i, r in enumerate(L.rows()):
    unweighted = [r[j] // weights[j] for j in range(6)]
    val_a = (unweighted[0]*a[0]^2 + unweighted[1]*a[0]*a[1] + unweighted[2]*a[0]*a[2] +
             unweighted[3]*a[1]^2 + unweighted[4]*a[1]*a[2] + unweighted[5]*a[2]^2)
    val_b = (unweighted[0]*b[0]^2 + unweighted[1]*b[0]*b[1] + unweighted[2]*b[0]*b[2] +
             unweighted[3]*b[1]^2 + unweighted[4]*b[1]*b[2] + unweighted[5]*b[2]^2)
    print(f"Row {i}: norm bits = {vector(r).norm().n().log(2):.1f}, val_a = {val_a}, val_b = {val_b}")
