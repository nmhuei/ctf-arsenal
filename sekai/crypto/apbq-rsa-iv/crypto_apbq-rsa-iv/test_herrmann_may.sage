import random
from Crypto.Util.number import getPrime

# Test on toy instance
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
print("x_true:", x_true)
print("gcd(x . h, n):", gcd(vector(x_true) * vector(h), n) in (p, q))
