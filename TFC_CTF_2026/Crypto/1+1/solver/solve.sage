import sys, os
from Crypto.Util.number import long_to_bytes

chall_dir = "/home/light/Workspace/CTF/TFC_CTF_2026/Crypto/1+1/challenge"
sys.path.insert(0, chall_dir)
import output

xs = output.xs
n = len(xs)
x0 = xs[0]

# ACDP / Simultaneous Diophantine Approximation
W = 2^512
C = 2^70

M = Matrix(ZZ, n, n)
M[0, 0] = W
for i in range(1, n):
    M[0, i] = C * xs[i]
    M[i, i] = -C * x0

L = M.LLL()

for row in L:
    if row[0] % W == 0 and row[0] != 0:
        q0 = abs(row[0] // W)
        p_cand = x0 // q0
        try:
            flag = long_to_bytes(p_cand).decode()
            if flag.startswith("TFCCTF{"):
                print("FOUND FLAG:", flag)
                with open("/home/light/Workspace/CTF/TFC_CTF_2026/Crypto/1+1/flag.txt", "w") as f:
                    f.write(flag)
                break
        except Exception:
            pass
