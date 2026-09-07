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
mono_objs = [x0^i0 * x1^i1 * x2^i2 for i0, i1, i2 in monomials]
M = Matrix(ZZ, dim, dim)
for r in range(dim):
    for c in range(dim):
        M[r, c] = polys[r].monomial_coefficient(mono_objs[c]) * (X^d)

L = M.LLL()

P1 = sum((L[0, c] // (X^d)) * mono_objs[c] for c in range(dim))
P2 = sum((L[1, c] // (X^d)) * mono_objs[c] for c in range(dim))

print("P1:", P1)
print("P2:", P2)

print("P1 factor:", P1.factor())
print("P2 factor:", P2.factor())
linear_factor = list(P1.factor())[0][0]
print("linear factor:", linear_factor)
c0 = linear_factor.monomial_coefficient(x0)
c1 = linear_factor.monomial_coefficient(x1)
c2 = linear_factor.monomial_coefficient(x2)

print("b:", b)
print("c:", [c0, c1, c2])
print("c0/b0:", QQ(c0)/QQ(b[0]))
print("c1/b1:", QQ(c1)/QQ(b[1]))
print("c2/b2:", QQ(c2)/QQ(b[2]))
print("Proportional?:", QQ(c0)/QQ(b[0]) == QQ(c1)/QQ(b[1]) == QQ(c2)/QQ(b[2]))

# If c is proportional to b, then c is b (up to scalar)!
# And if we know b, we factor n immediately!
# Let's check gcd(c0*h1 - c1*h0, n):
g = gcd(c0*h[1] - c1*h[0], n)
print("gcd(c0*h1 - c1*h0, n):", g)
print("p:", p)
print("Factored?:", g in (p, q))
