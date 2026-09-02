import requests
from client import GhostClient

c = GhostClient()
c.bootstrap()

paths = [
    "/api/healthz",
    "/api/search/help",
    "/api/archive/recent",
    "/api/session/guest",
    "/api/transport/bootstrap",
    "/api/gateway",
    "/api/admin",
    "/api/login",
    "/api/auth",
    "/api/auth/login",
    "/api/flag",
    "/api/user",
    "/api/users",
    "/api/logs",
    "/api/config",
    "/api/debug",
    "/api/version",
    "/api/status",
    "/api/swagger",
    "/api/openapi.json",
    "/api/docs",
    "/test",
    "/test/",
    "/flag",
    "/flag.txt",
    "/env",
    "/.env",
]

for p in paths:
    url = f"https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf{p}"
    r1 = requests.get(url, headers={"Authorization": f"Bearer {c.token}"})
    r2 = requests.post(url, headers={"Authorization": f"Bearer {c.token}"})
    print(f"{p:30s} -> GET: {r1.status_code} ({len(r1.content)}B) | POST: {r2.status_code} ({len(r2.content)}B)")
