import requests

base = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

r = requests.get(f"{base}/health")
print("GET /health ->", r.status_code, r.text)

r2 = requests.get(f"{base}/healthz")
print("GET /healthz ->", r2.status_code, r2.text)
