"""
Check if the recovered RSA modulus N is weak/factorable.
Use SageMath for factorization attempts.
Run with: sage check_rsa_weak.py
"""
import json

# Load N from recovered_n.txt
with open("recovered_n.txt", "r") as f:
    N = Integer(int(f.read().strip(), 16))

print(f"N = {hex(int(N))[:60]}...")
print(f"N bits: {N.nbits()}")

# Check if N is a perfect power
print("\nChecking if N is a perfect power...")
pp = N.is_perfect_power()
print(f"  Perfect power: {pp}")

# Check small factor
print("\nChecking small prime factors (up to 10^6)...")
for p in primes(10**6):
    if N % p == 0:
        print(f"  FOUND SMALL FACTOR: {p}")
        q = N // p
        print(f"  q = {q}")
        print(f"  q is prime: {q.is_prime()}")
        break
else:
    print("  No small factors found")

# Check Fermat factorization (close primes)
print("\nTrying Fermat factorization...")
import time
t0 = time.time()
a = isqrt(N) + 1
for i in range(10**6):
    b2 = a*a - N
    if b2 >= 0:
        b = isqrt(b2)
        if b*b == b2:
            p = a - b
            q = a + b
            print(f"  FERMAT FACTORED! p*q = N")
            print(f"  p = {p}")
            print(f"  q = {q}")
            break
    a += 1
else:
    print(f"  Fermat failed after {10**6} iterations ({time.time()-t0:.1f}s)")

# Check factordb
print("\nChecking factordb.com...")
import requests
try:
    r = requests.get(f"http://factordb.com/api?query={int(N)}", timeout=10)
    data = r.json()
    status = data.get("status", "?")
    factors = data.get("factors", [])
    print(f"  Status: {status}")
    print(f"  Factors: {factors}")
except Exception as e:
    print(f"  Error: {e}")

# Try Williams p+1 and Pollard p-1
print("\nTrying Pollard p-1...")
t0 = time.time()
try:
    # Quick Pollard p-1 with small bound
    B = 10**5
    a = Integer(2)
    for p in primes(B):
        pp = p
        while pp < B:
            a = power_mod(a, p, N)
            pp *= p
    g = gcd(a - 1, N)
    if 1 < g < N:
        print(f"  POLLARD p-1 FACTORED!")
        print(f"  factor: {g}")
        print(f"  cofactor: {N // g}")
    else:
        print(f"  Pollard p-1 failed with B={B} ({time.time()-t0:.1f}s)")
except Exception as e:
    print(f"  Error: {e}")

# Try ECM (if available)
print("\nTrying ECM factorization (limited)...")
t0 = time.time()
try:
    result = ecm.factor(N, B1=10000, algorithm="ecm")
    print(f"  ECM result: {result}")
except Exception as e:
    print(f"  ECM: {e}")

print("\nDone.")
