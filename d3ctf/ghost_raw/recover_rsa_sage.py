"""
RSA public key recovery from JWT signatures using SageMath.
Run with: conda activate sage && sage recover_rsa_sage.py
"""
import hashlib
import base64
import json
import requests
import time

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

# Collect tokens
print("Collecting JWT tokens...")
tokens = []
for i in range(3):
    r = requests.post(f"{BASE}/api/session/guest", headers={"Accept": "application/json"})
    tokens.append(r.json()["token"])
    parts = tokens[-1].split('.')
    payload = json.loads(b64url_decode(parts[1]))
    print(f"  Token {i}: jti={payload.get('jti','?')}")

e = 65537
pairs = []
for t in tokens:
    parts = t.split('.')
    msg = (parts[0] + '.' + parts[1]).encode('ascii')
    sig = b64url_decode(parts[2])
    s_int = Integer(int.from_bytes(sig, 'big'))
    m_int = Integer(pkcs1_v15_encode(msg, len(sig)))
    pairs.append((s_int, m_int))

print(f"\nKey size: {len(b64url_decode(tokens[0].split('.')[2])) * 8} bits")
print(f"e = {e}")

# Compute X_i = s_i^e - m_i
# SageMath Integer handles this much faster
Xs = []
for i, (s, m) in enumerate(pairs):
    t0 = time.time()
    se = s ** e
    x = se - m
    elapsed = time.time() - t0
    print(f"  X[{i}] computed in {elapsed:.1f}s ({x.nbits()} bits)")
    Xs.append(x)

# GCD
print("\nComputing GCD...")
t0 = time.time()
n_candidate = gcd(Xs[0], Xs[1])
for i in range(2, len(Xs)):
    n_candidate = gcd(n_candidate, Xs[i])
print(f"GCD computed in {time.time()-t0:.1f}s, {n_candidate.nbits()} bits")

# Remove small prime factors
for p in primes(10000):
    while n_candidate % p == 0:
        n_candidate //= p

n = int(n_candidate)
print(f"\nRecovered N: {n.bit_length()} bits")

if 2040 <= n.bit_length() <= 2056:
    print("VALID RSA MODULUS!")
    
    # Verify
    for i, (s, m) in enumerate(pairs):
        ok = pow(int(s), e, n) == int(m)
        print(f"  Verify token {i}: {ok}")
    
    # Save as PEM
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
    from cryptography.hazmat.primitives import serialization
    pub = RSAPublicNumbers(e, n).public_key()
    pem = pub.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    with open("recovered_pubkey.pem", "wb") as f:
        f.write(pem)
    print(f"\nSaved to recovered_pubkey.pem")
    print(pem.decode())
    
    # Also save N in hex for reference
    with open("recovered_n.txt", "w") as f:
        f.write(hex(n))
    print(f"N (hex): {hex(n)[:60]}...")
else:
    print(f"N is {n.bit_length()} bits - unexpected size")
    print(f"N (hex): {hex(n)[:100]}...")
