import requests
import json

base = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

# Test POST /api/auth/ticket
r1 = requests.post(
    f"{base}/api/auth/ticket",
    headers={"Content-Type": "application/json", "Accept": "application/json"},
    json={"principal": "ops-root", "mode": "bootstrap", "credentialType": "temporary"}
)
print("POST /api/auth/ticket ->", r1.status_code, r1.text)

# Test POST /api/auth/exchange
if r1.status_code == 200:
    data = r1.json()
    ticket = data.get("exchangeTicket") or data.get("ticket")
    r2 = requests.post(
        f"{base}/api/auth/exchange",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json={"ticket": ticket, "grantType": "legacy-bootstrap"}
    )
    print("POST /api/auth/exchange ->", r2.status_code, r2.text)
