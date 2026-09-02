import requests
import time
import urllib3

urllib3.disable_warnings()
ACTIVE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

def check_ep(path, method="GET", **kwargs):
    time.sleep(2.5)
    while True:
        try:
            r = s.request(method, f"{ACTIVE_URL}{path}", timeout=10, **kwargs)
            if r.status_code in [502, 503]:
                time.sleep(3.5)
                continue
            return r.status_code, len(r.content), r.headers.get("Content-Type", ""), r.text[:80]
        except Exception as e:
            time.sleep(3.5)

endpoints = [
    "/",
    "/api/status",
    "/api/authenticate",
    "/api/models",
    "/api/inference",
    "/api/generate",
    "/api/chat",
    "/api/predict",
    "/v1/models",
    "/v1/chat/completions",
    "/v1/completions",
    "/api/v1/models",
    "/api/v1/chat/completions",
    "/models",
    "/inference",
    "/docs",
    "/openapi.json"
]

print("=== Checking routes on active instance ===")
for ep in endpoints:
    st_g, len_g, ct_g, txt_g = check_ep(ep, method="GET")
    print(f"GET  {ep:25s} -> {st_g} ({len_g}b, {ct_g}): {txt_g.strip()}")
    st_p, len_p, ct_p, txt_p = check_ep(ep, method="POST", json={"token": "0"*48})
    print(f"POST {ep:25s} -> {st_p} ({len_p}b, {ct_p}): {txt_p.strip()}")
