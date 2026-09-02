#!/usr/bin/env python3
import random, math, sys
from pathlib import Path
from sympy import isprime

ROOT = Path(__file__).resolve().parent / 'rrssaa-ecsc-2023-norway'
if not ROOT.exists():
    ROOT = Path('/mnt/data/rrssaa/rrssaa-ecsc-2023-norway')
out = (ROOT/'files/output_db592c010295033ed6308f623264ba63.txt').read_text().strip().split()
N, c = map(lambda x:int(x,16), out)
e = 0x10001

def get_prime_from_seed(seed):
    r = random.Random()
    r.seed(seed)
    p = 1
    while not isprime(p):
        p = r._randbelow(2**256) | 1
    return int(p)

def crt_pair(a1, m1, a2, m2):
    # m1,m2 coprime
    t = ((a2-a1) * pow(m1, -1, m2)) % m2
    return a1 + m1*t, m1*m2

factors = []
M = 1
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
for seed in range(limit):
    p = get_prime_from_seed(seed)
    g = math.gcd(p, N)
    if g != 1 and g not in factors:
        factors.append(g)
        M *= g
        print(f'[+] seed={seed:<6d} factor bits={g.bit_length()} known_product_bits={M.bit_length()}')
        # Need > 128 bytes; add margin
        if M.bit_length() > 8*128:
            break

if M.bit_length() <= 8*128:
    print(f'[-] not enough modulus collected ({M.bit_length()} bits). Increase limit.')
    sys.exit(1)

x = 0
mod = 1
for p in factors:
    d = pow(e, -1, p-1)
    mp = pow(c % p, d, p)
    x, mod = crt_pair(x, mod, mp, p)

m = x
flag = m.to_bytes((m.bit_length()+7)//8, 'big')
print('[+] recovered bytes:', flag)
try:
    print(flag.decode())
except UnicodeDecodeError:
    pass
