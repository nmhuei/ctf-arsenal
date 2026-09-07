import random
from Crypto.Util.number import getPrime

p = getPrime(60)
q = getPrime(60)
n = p * q
B = 2**18

a = vector(ZZ, [random.randint(1, B) for _ in range(3)])
b = vector(ZZ, [random.randint(1, B) for _ in range(3)])
h = a*p + b*q

M = Matrix(ZZ, [
    list(h),
    [n, 0, 0],
    [0, n, 0],
    [0, 0, n]
])
HNF = M.hermite_form()
HNF_rows = [r for r in HNF.rows() if vector(r).norm() > 0]
L = Matrix(ZZ, HNF_rows).LLL()

H = vector(ZZ, h)
pa = vector(ZZ, [a[i]*p for i in range(3)])
qb = vector(ZZ, [b[i]*q for i in range(3)])

c = vector(ZZ, [ZZ(x) for x in L.solve_left(H)])
u = vector(ZZ, [ZZ(x) for x in L.solve_left(pa)])
v = vector(ZZ, [ZZ(x) for x in L.solve_left(qb)])

w = u - v

print("c:", c)
print("u:", u)
print("v:", v)
print("w:", w)

ks = [(L[i][0] * pow(int(h[0]), -1, n)) % n for i in range(3)]

R.<w0, w1, w2> = ZZ[]

# 1. E0:
E0 = (ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1

# 2. E1, E2, E3:
polys = [E0]
for j in range(3):
    Ej = (w0*L[0, j] + w1*L[1, j] + w2*L[2, j])^2 - H[j]^2
    polys.append(Ej)

print("Checking that all 4 polynomials vanish mod n at w:")
for idx, poly in enumerate(polys):
    val = poly(w[0], w[1], w[2])
    print(f"Poly {idx} val % n == 0:", val % n == 0)

# Check factorization via J:
J = (ks[0]*w[0] + ks[1]*w[1] + ks[2]*w[2]) % n
print("J^2 % n == 1:", (J^2) % n == 1)
print("gcd(J - 1, n) == p:", gcd(J - 1, n) == p, "or q:", gcd(J - 1, n) == q)
print("gcd(J + 1, n) == p:", gcd(J + 1, n) == p, "or q:", gcd(J + 1, n) == q)
