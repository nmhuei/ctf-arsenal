#!/usr/bin/env sage
from sage.all import *
from Crypto.Util.number import long_to_bytes
from pathlib import Path

output_file = Path(__file__).resolve().parent.parent / "challenge" / "crypto_nrt" / "output.txt"

with open(output_file) as f:
    text = f.read()

ns = {}
exec(text, ns)
N = ns["N"]
e = ns["e"]
ct = ns["ct"]

# Factor small 24-bit primes using Sage trial division / ECM limit
fac = factor(N, limit=2**24)
primes = []
for pr, _ in fac:
    if pr.bit_length() <= 25:
        primes.append(pr)

rem = [pow(ct, inverse_mod(e, p - 1), p) for p in primes]
m = crt(rem, primes)
flag = long_to_bytes(int(m))
print(f"[+] FLAG: {flag.decode()}")
