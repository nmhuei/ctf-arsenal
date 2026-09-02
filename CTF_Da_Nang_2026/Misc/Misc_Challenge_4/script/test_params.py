import requests
import urllib3
import time
import string

urllib3.disable_warnings()
BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

def send(payload, delay=3.0):
    time.sleep(delay)
    while True:
        try:
            r = s.post(f"{BASE_URL}/api/authenticate", json=payload, timeout=10)
            if r.status_code == 502:
                time.sleep(3.5)
                continue
            return r.status_code, r.text, dict(r.headers)
        except Exception as e:
            time.sleep(3.5)

print("=== 1. Thử các định dạng JSON khác nhau xem có phản hồi khác lạ không ===")
tests = [
    {"token": "0"*48, "token": "1"*48}, # duplicate key
    {"token": "0"*48, "verbose": 1},
    {"token": "0"*48, "debug": 1},
    {"token": "0"*48, "show": 1},
    {"token": "0"*48, "hint": 1},
    {"token": "0"*48, "admin": 1},
    {"token": "0"*48, "check": 1},
    {"token": "0"*48, "mode": "debug"},
    {"token": "0"*48, "mode": "test"},
]

for t in tests:
    st, body, hdrs = send(t)
    print(f"Payload {t} -> Status {st}, Body: {body.strip()}")
