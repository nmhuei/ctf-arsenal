import requests
import urllib3
import time

urllib3.disable_warnings()
BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

endpoints = [
    "/robots.txt",
    "/.git/HEAD",
    "/api",
    "/api/",
    "/api/docs",
    "/api/openapi.json",
    "/api/swagger.json",
    "/api/models",
    "/api/status",
    "/api/health",
    "/api/token",
    "/api/inference",
    "/api/v1",
    "/static/ctfd-theme.css",
    "/console",
    "/admin",
    "/flag",
]

for ep in endpoints:
    time.sleep(1.0)
    try:
        r = s.get(f"{BASE_URL}{ep}", timeout=5)
        print(f"GET {ep} -> {r.status_code} (len={len(r.content)})")
    except Exception as e:
        print(f"GET {ep} -> err {e}")
