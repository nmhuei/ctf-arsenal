import requests
import urllib3
import json
import time

urllib3.disable_warnings()
BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

def send_and_inspect(label, url, method="POST", **kwargs):
    time.sleep(3.0)
    while True:
        try:
            t0 = time.perf_counter()
            r = s.request(method, url, timeout=10, **kwargs)
            dt = (time.perf_counter() - t0) * 1000
            if r.status_code == 502:
                time.sleep(3.5)
                continue
            print(f"=== {label} ===")
            print(f"Status: {r.status_code}")
            print(f"Time: {dt:.2f}ms")
            print("Headers:")
            for k, v in r.headers.items():
                print(f"  {k}: {v}")
            print(f"Raw body ({len(r.content)} bytes): {repr(r.content)}")
            print("-" * 50)
            return r
        except Exception as e:
            time.sleep(3.5)

# 1. Inspect different 48-char tokens
send_and_inspect("All zeros 48", f"{BASE_URL}/api/authenticate", json={"token": "0" * 48})
send_and_inspect("All As 48", f"{BASE_URL}/api/authenticate", json={"token": "A" * 48})
send_and_inspect("All as 48", f"{BASE_URL}/api/authenticate", json={"token": "a" * 48})
send_and_inspect("Mixed 1234...48", f"{BASE_URL}/api/authenticate", json={"token": "1234567890abcdef" * 3})

# 2. Check other API paths with different methods
send_and_inspect("GET /api/status", f"{BASE_URL}/api/status", method="GET")
send_and_inspect("HEAD /api/status", f"{BASE_URL}/api/status", method="HEAD")
send_and_inspect("POST /api/status", f"{BASE_URL}/api/status", json={})
send_and_inspect("GET /api/authenticate", f"{BASE_URL}/api/authenticate", method="GET")
