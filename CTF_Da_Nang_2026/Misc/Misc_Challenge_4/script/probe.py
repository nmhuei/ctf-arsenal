import requests
import json
import time
import urllib3

urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

def test(payload):
    time.sleep(0.5)
    t0 = time.perf_counter()
    try:
        r = s.post(f"{BASE_URL}/api/authenticate", json=payload, timeout=10)
        dt = (time.perf_counter() - t0) * 1000
        print(f"Payload: {payload} -> Status: {r.status_code}, Time: {dt:.2f}ms, Body: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

print("--- Testing different payloads ---")
test({})
test({"token": ""})
test({"token": "a"})
test({"token": "a" * 47})
test({"token": "a" * 48})
test({"token": "a" * 49})
test({"token": "0" * 48})
test({"token": "A" * 48})
test({"token": "!" * 48})
