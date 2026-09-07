import random
from Crypto.Util.number import getPrime

p = getPrime(60)
q = getPrime(60)
n = p * q
B = 2**18

a = [random.randint(1, B) for _ in range(3)]
b = [random.randint(1, B) for _ in range(3)]
h = [a[i]*p + b[i]*q for i in range(3)]

A1 = (h[1] * pow(h[0], -1, n)) % n
A2 = (h[2] * pow(h[0], -1, n)) % n

Mb = Matrix(ZZ, [[b[0], b[1], b[2]]]).right_kernel().basis_matrix().LLL()
x_true = Mb[0]

inv_A2 = pow(A2, -1, n)
c1 = (A1 * inv_A2) % n
c0 = (1 * inv_A2) % n

R.<x0, x1, x2> = ZZ[]
f = x2 + c1 * x1 + c0 * x0

m = 2
d = 2
X = 2**10

# Generate all monomials of degree d with order x2 > x1 > x0:
monomials = []
for i2 in range(d, -1, -1):
    for i1 in range(d - i2, -1, -1):
        i0 = d - i2 - i1
        monomials.append((i0, i1, i2))

polys = []
for i0, i1, i2 in monomials:
    if i2 < m:
        poly = (x0^i0) * (x1^i1) * (f^i2) * (n^(m - i2))
    else:
        poly = (x0^i0) * (x1^i1) * (x2^(i2 - m)) * (f^m)
    polys.append(poly)

dim = len(monomials)
print(f"Dimension: {dim}x{dim}")

# Build matrix:
mono_objs = [x0^i0 * x1^i1 * x2^i2 for i0, i1, i2 in monomials]
M = Matrix(ZZ, dim, dim)
for r in range(dim):
    for c in range(dim):
        M[r, c] = polys[r].monomial_coefficient(mono_objs[c]) * (X^d)

print("Matrix is triangular:", M.is_triangular())
print("Running LLL...")
L = M.LLL()

print("Checking LLL rows for vanishing at x_true:")
found = 0
for r in range(dim):
    poly = sum((L[r, c] // (X^d)) * mono_objs[c] for c in range(dim))
    val = poly(x_true[0], x_true[1], x_true[2])
    if val == 0:
        found += 1
        print(f"Row {r} vanishes at x_true! Norm bits: {vector(L[r]).norm().n().log(2):.1f}")

print(f"Total vanishing rows: {found}")
