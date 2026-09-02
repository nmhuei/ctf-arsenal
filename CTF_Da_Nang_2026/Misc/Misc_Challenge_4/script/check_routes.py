import requests
import time
import urllib3

urllib3.disable_warnings()
BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

def check(url, method="GET", **kwargs):
    time.sleep(3.0)
    while True:
        try:
            r = s.request(method, url, timeout=10, **kwargs)
            if r.status_code == 502:
                time.sleep(3.5)
                continue
            return r.status_code, len(r.content), r.text
        except Exception as e:
            time.sleep(3.5)

endpoints = [
    "/api/v2.4.0",
    "/api/v3.1.0",
    "/api/v2.4.0/authenticate",
    "/api/v3.1.0/authenticate",
    "/api/v2/authenticate",
    "/api/v3/authenticate",
    "/api/v1/authenticate",
    "/api/token",
    "/api/tokens",
    "/api/auth/token",
    "/api/secret",
    "/api/secrets",
    "/api/gateway",
    "/api/gateway/status",
    "/api/gateway/token",
    "/api/inference/token",
    "/api/debug/token",
    "/api/version",
    "/version",
    "/api/info",
    "/info",
    "/api/models/status",
    "/api/models/token"
]

print("=== Checking potential versioned / hidden endpoints ===")
for ep in endpoints:
    st_get, l_get, t_get = check(f"{BASE_URL}{ep}", method="GET")
    print(f"GET  {ep:30s} -> {st_get} ({l_get}b): {t_get[:60].strip()}")
    st_post, l_post, t_post = check(f"{BASE_URL}{ep}", method="POST", json={"token": "0"*48})
    print(f"POST {ep:30s} -> {st_post} ({l_post}b): {t_post[:60].strip()}")
