import requests
import json
import time
import urllib3

urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

def inspect_req(desc, method, url, **kwargs):
    time.sleep(3.0)
    try:
        r = s.request(method, url, timeout=10, **kwargs)
        print(f"=== {desc} ===")
        print(f"Status: {r.status_code}")
        print(f"Headers: {json.dumps(dict(r.headers), indent=2)}")
        print(f"Cookies: {r.cookies.get_dict()}")
        print(f"Body: {r.text}")
        print("-" * 50)
    except Exception as e:
        print(f"=== {desc} === ERROR: {e}")

# 1. Inspect failed requests on /api/authenticate
inspect_req("Standard invalid token 48 chars", "POST", f"{BASE_URL}/api/authenticate", json={"token": "A"*48})
inspect_req("Token 48 zeroes", "POST", f"{BASE_URL}/api/authenticate", json={"token": "0"*48})
inspect_req("Token with prefix test", "POST", f"{BASE_URL}/api/authenticate", json={"token": "FLAG"*12})

# 2. Inspect failed requests on other endpoints
inspect_req("GET /api/authenticate", "GET", f"{BASE_URL}/api/authenticate")
inspect_req("GET /api/status", "GET", f"{BASE_URL}/api/status")
inspect_req("POST /api/status", "POST", f"{BASE_URL}/api/status", json={})
inspect_req("GET /nonexistent", "GET", f"{BASE_URL}/nonexistent")
