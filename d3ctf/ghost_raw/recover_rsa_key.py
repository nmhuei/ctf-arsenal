"""
Use a much more efficient approach: instead of computing s^e directly,
we use the modular arithmetic approach.

For RSA key recovery from signatures, the standard approach is:
1. Collect multiple (message, signature) pairs
2. Compute X_i = S_i^e - H_i (where H_i is the padded hash)
3. N = GCD(X_0, X_1, ...)

The problem is S_i^e is enormous (~134M bits for e=65537, s=2048 bits).

TRICK: Use the GCD calculation DURING exponentiation.
Actually, a better known approach: 
  N divides (s1^e * m2 - s2^e * m1) and N divides (s1^e - m1)
  
But really for CTF, let's use the portswigger/jwt_forgery approach
or manually compute using gmpy2 which handles big integers much faster.
"""
import subprocess
import sys

# Check if gmpy2 is available
try:
    import gmpy2
    print("gmpy2 is available!")
    HAS_GMPY2 = True
except ImportError:
    print("gmpy2 not available, trying to install...")
    subprocess.run([sys.executable, "-m", "pip", "install", "gmpy2"], capture_output=True)
    try:
        import gmpy2
        HAS_GMPY2 = True
        print("gmpy2 installed successfully!")
    except ImportError:
        HAS_GMPY2 = False
        print("gmpy2 not available, falling back to pure Python")

import hashlib
import base64
import json
import requests
import math

BASE = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

def b64url_decode(s):
    return base64.urlsafe_b64decode(s + '=' * ((4 - len(s) % 4) % 4))

SHA256_DIGEST_INFO = bytes.fromhex("3031300d060960864801650304020105000420")

def pkcs1_v15_encode(msg_bytes, key_size_bytes):
    h = hashlib.sha256(msg_bytes).digest()
    t = SHA256_DIGEST_INFO + h
    ps_len = key_size_bytes - len(t) - 3
    em = b'\x00\x01' + (b'\xff' * ps_len) + b'\x00' + t
    return int.from_bytes(em, 'big')

# Collect 2 tokens
print("Collecting tokens...")
tokens = []
for i in range(2):
    r = requests.post(f"{BASE}/api/session/guest", headers={"Accept": "application/json"})
    tokens.append(r.json()["token"])
    print(f"  Token {i} collected")

e = 65537
pairs = []
for t in tokens:
    parts = t.split('.')
    msg = (parts[0] + '.' + parts[1]).encode('ascii')
    sig = b64url_decode(parts[2])
    s_int = int.from_bytes(sig, 'big')
    m_int = pkcs1_v15_encode(msg, len(sig))
    pairs.append((s_int, m_int))

if HAS_GMPY2:
    print("Using gmpy2 for fast computation...")
    s0 = gmpy2.mpz(pairs[0][0])
    m0 = gmpy2.mpz(pairs[0][1])
    s1 = gmpy2.mpz(pairs[1][0])
    m1 = gmpy2.mpz(pairs[1][1])
    
    print("Computing s0^e...")
    s0e = gmpy2.powmod(s0, e, s0**e)  # This doesn't help...
    # Actually we need s^e exactly, not modular
    
    # Better: compute s0^e using gmpy2 pow
    import time
    t0 = time.time()
    s0e = pow(s0, e)
    print(f"s0^e computed in {time.time()-t0:.1f}s, {gmpy2.bit_length(s0e)} bits")
    
    x0 = s0e - m0
    
    t0 = time.time()
    s1e = pow(s1, e)
    print(f"s1^e computed in {time.time()-t0:.1f}s, {gmpy2.bit_length(s1e)} bits")
    
    x1 = s1e - m1
    
    print("Computing GCD...")
    t0 = time.time()
    n = gmpy2.gcd(x0, x1)
    print(f"GCD computed in {time.time()-t0:.1f}s")
    
    # Remove small factors
    for p in range(2, 10000):
        while n % p == 0:
            n //= p
    
    n = int(n)
    print(f"N: {n.bit_length()} bits")
    
    if 2040 <= n.bit_length() <= 2056:
        print("Valid RSA modulus recovered!")
        for i, (s, m) in enumerate(pairs):
            ok = pow(s, e, n) == m
            print(f"  Verify {i}: {ok}")
        
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
        from cryptography.hazmat.primitives import serialization
        pub = RSAPublicNumbers(e, n).public_key()
        pem = pub.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        with open("recovered_pubkey.pem", "wb") as f:
            f.write(pem)
        print("Saved to recovered_pubkey.pem")
        print(pem.decode())
    else:
        print(f"N is {n.bit_length()} bits, not 2048. Trying more tokens...")
else:
    print("Cannot proceed without gmpy2 for reasonable performance")
    print("Attempting pure Python (may take very long)...")
    
    import time
    t0 = time.time()
    s0e = pow(pairs[0][0], e)
    print(f"s0^e: {time.time()-t0:.1f}s, {s0e.bit_length()} bits")
    
    x0 = s0e - pairs[0][1]
    
    t0 = time.time()
    s1e = pow(pairs[1][0], e)
    print(f"s1^e: {time.time()-t0:.1f}s")
    
    x1 = s1e - pairs[1][1]
    
    print("Computing GCD...")
    n = math.gcd(x0, x1)
    
    for p in range(2, 10000):
        while n % p == 0:
            n //= p
    
    print(f"N: {n.bit_length()} bits")
