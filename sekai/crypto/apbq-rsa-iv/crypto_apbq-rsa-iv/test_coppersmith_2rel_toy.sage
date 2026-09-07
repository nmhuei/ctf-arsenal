# Toy test of Coppersmith for 2 linear relations mod p
p = random_prime(2^100)
q = random_prime(2^100)
n = p * q

# Secret root:
X_bound = 2^30
b0 = randint(1, X_bound)
b1 = randint(1, X_bound)
b2 = randint(1, X_bound)

a1 = (b1 * pow(b0, -1, p)) % p
a2 = (b2 * pow(b0, -1, p)) % p

alpha1 = crt([int(a1), randint(1, q-1)], [int(p), int(q)])
alpha2 = crt([int(a2), randint(1, q-1)], [int(p), int(q)])

print("Toy setup complete!")
print("b0, b1, b2 bits:", b0.bit_length(), b1.bit_length(), b2.bit_length())

# Polynomials in x0, x1, x2:
R.<x0, x1, x2> = PolynomialRing(ZZ)
f1 = x1 - alpha1 * x0
f2 = x2 - alpha2 * x0

monos = [R(1), x0, x1, x2, x0^2, x0*x1, x0*x2, x1^2, x1*x2, x2^2]
polys = [
    R(n),
    n * x0,
    n * x0^2,
    f1,
    f1 * x0,
    f2,
    f2 * x0,
    f1^2,
    f1 * f2,
    f2^2
]

# Check that all polys vanish mod p at (b0, b1, b2):
for idx, poly in enumerate(polys):
    val = poly(b0, b1, b2)
    assert val % p == 0, f"Poly {idx} does not vanish mod p!"
print("[+] All 10 polynomials vanish mod p at the secret root!")

# Build 10x10 matrix:
X = 2^32
weights = [X^(m.total_degree()) for m in monos]
M = Matrix(ZZ, 10, 10)
for i, poly in enumerate(polys):
    for j, m in enumerate(monos):
        M[i, j] = poly.monomial_coefficient(m) * weights[j]

print("[*] Running LLL...")
L_red = M.LLL()
print("[+] LLL done!")

for idx, r in enumerate(L_red.rows()[:3]):
    poly_cand = sum((r[j] // weights[j]) * monos[j] for j in range(10))
    val = poly_cand(b0, b1, b2)
    norm_bits = vector(r).norm().n().log(2)
    print(f"Row {idx}: norm bits = {norm_bits:.1f}, poly(root) == 0? {val == 0}")
