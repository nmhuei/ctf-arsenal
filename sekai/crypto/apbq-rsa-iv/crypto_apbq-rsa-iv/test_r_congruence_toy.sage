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

pa = vector(ZZ, [a[i]*p for i in range(3)])
u = vector(ZZ, [ZZ(x) for x in L.solve_left(pa)])

# u . L = p a => (u . L) = 0 mod p
# In particular: u0*L00 + u1*L10 + u2*L20 = 0 mod p:
val = (u[0]*L[0, 0] + u[1]*L[1, 0] + u[2]*L[2, 0])
print("val % p == 0:", val % p == 0)
print("val == p * a[0]:", val == p * a[0])

# Divide by L00 mod p:
# u0 + u1 * (L10 * inv_L00) + u2 * (L20 * inv_L00) = 0 mod p!
inv_L00 = pow(int(L[0, 0]), -1, n)
r1 = (L[1, 0] * inv_L00) % n
r2 = (L[2, 0] * inv_L00) % n

lin_val = (u[0] + u[1]*r1 + u[2]*r2) % n
print("lin_val % p == 0:", lin_val % p == 0)
print("lin_val % q == 0:", lin_val % q == 0)
print("gcd(lin_val, n) == p:", gcd(lin_val, n) == p)
