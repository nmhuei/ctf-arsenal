from sage.all import *

S = 2^368
X = 2^144

p, a, b, c, d = map(int, open("crypto_shredded-recipe/output.txt").read().split())

M = Matrix(ZZ, [
    [S*p,   0, 0, 0, 0],
    [S*a,   1, 0, 0, 0],
    [S*b,   0, 1, 0, 0],
    [S*c,   0, 0, 1, 0],
    [S*(-d), 0, 0, 0, X],
])

for r in M.LLL().rows():
    if abs(r[4]) == X:
        sign = 1 if r[4] == X else -1
        x = sign * r[1]
        y = sign * r[2]
        z = sign * r[3]
        xb = int(x).to_bytes(18, "big")
        yb = int(y).to_bytes(18, "big")
        zb = int(z).to_bytes(18, "big")
        flag = b"".join(bytes([xb[i], yb[i], zb[i]]) for i in range(18))
        open("flag.txt", "wb").write(flag)
        print("FLAG:", flag.decode())
        break
