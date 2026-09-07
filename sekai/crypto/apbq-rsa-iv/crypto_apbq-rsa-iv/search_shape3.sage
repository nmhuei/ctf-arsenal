import random
from Crypto.Util.number import getPrime

p = getPrime(60)
q = getPrime(60)
n = p * q
B = 2**18

a = [random.randint(1, B) for _ in range(3)]
b = [random.randint(1, B) for _ in range(3)]
h = [a[i]*p + b[i]*q for i in range(3)]

R1 = (h[1] * pow(h[0], -1, n)) % n
R2 = (h[2] * pow(h[0], -1, n)) % n

for log2_K in range(0, 150, 5):
    K = 1 << log2_K
    M = Matrix(ZZ, [
        [K, R1, R2],
        [0, n, 0],
        [0, 0, n]
    ])
    L = M.LLL()
    for row in L.rows():
        x0 = row[0] // K
        # If x0 != 0:
        # Check comb:
        for comb in [row[0], row[1], row[2], x0*h[1] - row[1]*h[0], x0*h[2] - row[2]*h[0]]:
            g = gcd(int(comb), n)
            if 1 < g < n:
                print(f"Shape 3 succeeded with log2_K={log2_K}! Factor: {g}")
                break

for log2_K in range(0, 150, 5):
    K = 1 << log2_K
    M = Matrix(ZZ, [
        [K, 0, R1],
        [0, K, R2],
        [0, 0, n]
    ])
    L = M.LLL()
    for row in L.rows():
        for comb in row:
            g = gcd(int(comb), n)
            if 1 < g < n:
                print(f"Shape 4 succeeded with log2_K={log2_K}! Factor: {g}")
                break
