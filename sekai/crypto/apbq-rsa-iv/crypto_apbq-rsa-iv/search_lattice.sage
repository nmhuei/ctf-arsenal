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

# We want to find a matrix M such that LLL(M) has a row that gives p or q:
# What shapes could M have?
# Let's test several shapes:

# Shape 1:
# [K, h0, h1]
# [0, n,  0 ]
# [0, 0,  n ]
# for various K:
for log2_K in range(0, 150, 10):
    K = 1 << log2_K
    M = Matrix(ZZ, [
        [K, h[0] % n, h[1] % n, h[2] % n],
        [0, n, 0, 0],
        [0, 0, n, 0],
        [0, 0, 0, n]
    ])
    L = M.LLL()
    for row in L.rows():
        for val in row:
            if val != 0:
                g = gcd(int(val), n)
                if 1 < g < n:
                    print(f"Shape 1 succeeded with log2_K={log2_K}! Factor: {g}")
                    break

# Shape 2:
# 3 hints:
# [K, 0, 0, h0]
# [0, K, 0, h1]
# [0, 0, K, h2]
# [0, 0, 0, n ]
for log2_K in range(0, 150, 10):
    K = 1 << log2_K
    M = Matrix(ZZ, [
        [K, 0, 0, h[0] % n],
        [0, K, 0, h[1] % n],
        [0, 0, K, h[2] % n],
        [0, 0, 0, n]
    ])
    L = M.LLL()
    for row in L.rows():
        # Check gcd of linear combination:
        # row[0]//K * h0 + row[1]//K * h1 + row[2]//K * h2
        x0, x1, x2 = row[0]//K, row[1]//K, row[2]//K
        comb = x0*h[0] + x1*h[1] + x2*h[2]
        g = gcd(comb, n)
        if 1 < g < n:
            print(f"Shape 2 succeeded with log2_K={log2_K}! Factor: {g}")
            break
