import requests
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ec
import os

BASE_URL = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

def int_to_b64url(val: int, length: int) -> str:
    b = val.to_bytes(length, 'big')
    return base64.urlsafe_b64encode(b).decode('utf-8').rstrip('=')

for i in range(3):
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/session/guest", headers={"Accept": "application/json"})
    token = resp.json()["token"]

    priv_key = ec.generate_private_key(ec.SECP256R1())
    pub_key = priv_key.public_key()
    numbers = pub_key.public_numbers()
    
    jwk = {
        "kty": "EC",
        "crv": "P-256",
        "x": int_to_b64url(numbers.x, 32),
        "y": int_to_b64url(numbers.y, 32),
        "ext": True
    }

    resp = session.post(
        f"{BASE_URL}/api/transport/bootstrap",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={"clientPublicKey": jwk}
    )
    data = resp.json()
    print(f"Session {i}:")
    print("  sid:", data.get("sid"))
    print("  serverPublicKey:", data.get("serverPublicKey"))
    print("  salt:", data.get("salt"))
