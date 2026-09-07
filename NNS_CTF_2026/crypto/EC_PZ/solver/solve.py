#!/usr/bin/env sage
from sage.all import *
from Crypto.Util.number import long_to_bytes
from pathlib import Path

output_file = Path(__file__).resolve().parent.parent / "challenge" / "crypto_ec-pz" / "output.txt"

with open(output_file) as f:
    lines = [line.strip() for line in f if line.strip()]

ns = {}
for line in lines:
    k, v = line.split(" = ")
    ns[k] = eval(v)

P = ns["P"]
Q = ns["Q"]
R = ns["R"]
C = ns["C"]

x1, y1 = P
x2, y2 = Q
x3, y3 = R

num1 = (y2**2 - y1**2) - (x2**3 - x1**3)
den1 = x2 - x1

num2 = (y3**2 - y2**2) - (x3**3 - x2**3)
den2 = x3 - x2

rel1 = num1 * den2 - num2 * den1
rel2 = (3 * x1**2 * den1 + num1)**2 - 4 * y1**2 * (x2 + 2 * x1) * den1**2

p_cand = gcd(rel1, rel2)
p = None
for pr, _ in factor(p_cand):
    if pr.bit_length() > 200:
        p = pr
        break

assert p is not None, "Failed to recover p"
a = ((y2**2 - y1**2 - (x2**3 - x1**3)) * inverse_mod(x2 - x1, p)) % p
b = (y1**2 - x1**3 - a * x1) % p

E = EllipticCurve(GF(p), [a, b])
k = next_prime(0x133713371337)
F = inverse_mod(k, E.order()) * E(C)

flag = long_to_bytes(int(F.xy()[0]))
print(f"[+] FLAG: {flag.decode()}")
