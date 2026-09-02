import requests

base = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

endpoints = [
    "/.well-known/jwks.json",
    "/.well-known/jwks",
    "/.well-known/openid-configuration",
    "/jwks.json",
    "/jwks",
    "/api/jwks.json",
    "/api/jwks",
    "/api/keys",
    "/api/key",
    "/api/public-key",
    "/api/pubkey",
    "/keys",
    "/keys/primary-rs256",
    "/keys/primary-rs256.pem",
    "/keys/primary-rs256.pub",
    "/keys/primary-rs256.json",
    "/public.pem",
    "/pubkey.pem",
    "/key.pem",
]

for ep in endpoints:
    r = requests.get(f"{base}{ep}")
    if r.status_code != 404:
        print(f"FOUND {ep}: {r.status_code} -> {r.text[:200]}")
    else:
        print(f"404: {ep}")
