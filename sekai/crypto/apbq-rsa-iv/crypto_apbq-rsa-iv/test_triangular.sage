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

# Ensure x2 is not 0:
if x_true[2] == 0:
    print("x2 is 0, skip")
    exit()

# We want x2 + c1*x1 + c0*x0 = 0 mod p
inv_A2 = pow(A2, -1, n)
c1 = (A1 * inv_A2) % n
c0 = (1 * inv_A2) % n

R.<x0, x1, x2> = ZZ[]
f = x2 + c1 * x1 + c0 * x0

# Check that f(x_true) = 0 mod p:
val_true = f(x_true[0], x_true[1], x_true[2])
assert val_true % p == 0
print("val_true % p == 0: OK")
