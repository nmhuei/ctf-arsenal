import random
from Crypto.Util.number import getPrime

p = getPrime(60)
q = getPrime(60)
n = p * q
B = 2**18

a = [random.randint(1, B) for _ in range(3)]
b = [random.randint(1, B) for _ in range(3)]
h = [a[i]*p + b[i]*q for i in range(3)]

print("p =", p)
print("q =", q)
print("b =", b)
print("a =", a)

# Let's test what matrix with hints and K finds something!
# Candidates for matrix:
# 1. M1 = Matrix([[K, h0, h1, h2], [0, n, 0, 0], [0, 0, n, 0], [0, 0, 0, n]])
# 2. M2 = Matrix([[K, 0, h0], [0, K, h1], [0, 0, h2]])
# 3. M3 = Matrix([[K*h0, K*h1, K*h2], [n, 0, 0], [0, n, 0], [0, 0, n]])
# 4. M4 = Matrix([[K, h0], [0, h1]])
