import random
from Crypto.Util.number import getPrime

p = getPrime(60)
q = getPrime(60)
n = p * q
B = 2**36 # B ~ 36 bits, p ~ 60 bits, so B < p^(2/3) = 40 bits!

a = [random.randint(1, B) for _ in range(3)]
b = [random.randint(1, B) for _ in range(3)]
h = [a[i]*p + b[i]*q for i in range(3)]

R0 = (h[0] * pow(h[1], -1, n)) % n
R1 = (h[0] * pow(h[2], -1, n)) % n

# Check that b0 - R0*b1 = 0 mod p and b0 - R1*b2 = 0 mod p:
assert (b[0] - R0 * b[1]) % p == 0
assert (b[0] - R1 * b[2]) % p == 0
assert (a[0] - R0 * a[1]) % q == 0
assert (a[0] - R1 * a[2]) % q == 0

print("Congruences verified!")
