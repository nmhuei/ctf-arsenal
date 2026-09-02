#!/usr/bin/env sage
# Solver for TetCTF 2021 / CryptoHack "Unevaluated"
# Run: sage solver_unevaluated.sage

from collections import namedtuple
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes
from sage.all import pari
from math import isqrt

Complex = namedtuple("Complex", ["re", "im"])

def complex_mult(c1, c2, modulus):
    return Complex(
        (c1.re * c2.re - c1.im * c2.im) % modulus,
        (c1.re * c2.im + c1.im * c2.re) % modulus,
    )

def complex_pow(c, exp, modulus):
    result = Complex(1, 0)
    while exp > 0:
        if exp & 1:
            result = complex_mult(result, c, modulus)
        c = complex_mult(c, c, modulus)
        exp >>= 1
    return result

def norm(c, modulus):
    # Homomorphism: Norm(a + bi) = a^2 + b^2 mod n
    return (c.re * c.re + c.im * c.im) % modulus

# Challenge output
g = Complex(
    re=20878314020629522511110696411629430299663617500650083274468525283663940214962,
    im=16739915489749335460111660035712237713219278122190661324570170645550234520364,
)
order = 364822540633315669941067187619936391080373745485429146147669403317263780363306505857156064209602926535333071909491
n = 42481052689091692859661163257336968116308378645346086679008747728668973847769
public_key = Complex(
    re=11048898386036746197306883207419421777457078734258168057000593553461884996107,
    im=34230477038891719323025391618998268890391645779869016241994899690290519616973,
)
encrypted_flag = b'\'{\xda\xec\xe9\xa4\xc1b\x96\x9a\x8b\x92\x85\xb6&p\xe6W\x8axC)\xa7\x0f(N\xa1\x0b\x05\x19@<T>L9!\xb7\x9e3\xbc\x99\xf0\x8f\xb3\xacZ:\xb3\x1c\xb9\xb7;\xc7\x8a:\xb7\x10\xbd\x07"\xad\xc5\x84'

print("[+] Applying norm map")
ng = norm(g, n)
npub = norm(public_key, n)

print("[+] Solving DLP with PARI znlog")
k = int(pari(f"znlog({npub}, Mod({ng}, {n}))"))
assert pow(ng, k, n) == npub
print(f"[+] k mod subgroup_order = {k}")

# n = p^2 and the norm-subgroup order after generator^24 is p*(p-1)//2.
p = isqrt(n)
assert p * p == n
subgroup_order = int(p * (p - 1) // 2)
assert pow(ng, k + subgroup_order, n) == npub

print("[+] Trying AES keys k + i*subgroup_order")
for i in range(100):
    candidate = k + i * subgroup_order
    key = long_to_bytes(candidate, 32)
    flag = AES.new(key, AES.MODE_ECB).decrypt(encrypted_flag).rstrip(b"\x00")
    if b"TetCTF{" in flag:
        print(f"[+] offset i = {i}")
        print(flag.decode())
        break
else:
    raise RuntimeError("Flag not found; increase search range")
