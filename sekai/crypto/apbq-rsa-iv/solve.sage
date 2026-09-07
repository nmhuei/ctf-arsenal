import time
from sage.all import *
from Crypto.Util.number import long_to_bytes

t0 = time.time()
with open("crypto_apbq-rsa-iv/apbq-rsa-iv.py") as f:
    text = f.read()
exec(text.split("'''")[1])

inv2 = inverse_mod(hints[2], n)
F.<X,Y,Z> = QQ[]
h0_ratio = (hints[0] * inv2) % n
h1_ratio = (hints[1] * inv2) % n
f = vector([X - h0_ratio * Z, Y - h1_ratio * Z, Z^2 - hints[2]^2]) / n
arr = [f[0]^x * f[1]^y * f[2]^(z//2) * Z^(z%2) for i in range(5) for x,y,z in IntegerVectors(2*i+2, 3)]

CM, mon = Sequence(g - g(0,0,0) for g in arr).coefficients_monomials(sparse=False)
mat = CM * diagonal_matrix(mon(*hints), sparse=False)
print(f"[*] Matrix built in {time.time()-t0:.2f}s, shape: {mat.dimensions()}")

t1 = time.time()
print("[*] Running flatter on 160x160 lattice...")
lll = mat.LLL(algorithm="flatter")
print(f"[*] Flatter completed in {time.time()-t1:.2f}s!")

v = lll.solve_right(vector([0]*(len(mon)-1)+[1]))
p = gcd(n, 1 + sqrt(v[-7]/v[-1]-1)%n)
print(f"[+] Found p = {p}")

q = n // p
assert p * q == n
d = inverse_mod(e, (p - 1) * (q - 1))
m = pow(c, d, n)
flag = long_to_bytes(m)
print(f"[+] FLAG = {flag.decode()}")

with open("flag.txt", "w") as out_f:
    out_f.write(flag.decode().strip() + "\n")
