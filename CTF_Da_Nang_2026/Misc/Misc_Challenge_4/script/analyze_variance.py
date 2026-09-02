import requests
import urllib3
import time
import json

urllib3.disable_warnings()
ACTIVE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

def send(token, delay=2.5):
    time.sleep(delay)
    while True:
        try:
            r = s.post(f"{ACTIVE_URL}/api/authenticate", json={"token": token}, timeout=10)
            if r.status_code in [502, 503]:
                time.sleep(3.5)
                continue
            return r
        except Exception as e:
            time.sleep(3.5)

# Test different kinds of 48-char tokens
test_tokens = [
    ("all_0", "0" * 48),
    ("all_1", "1" * 48),
    ("all_9", "9" * 48),
    ("all_a", "a" * 48),
    ("all_z", "z" * 48),
    ("all_A", "A" * 48),
    ("all_Z", "Z" * 48),
    ("mix_1", "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKL"),
    ("mix_2", "LKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210"),
]

print("=== Analyzing exact raw responses ===")
for name, tok in test_tokens:
    r = send(tok)
    print(f"[{name}] Status: {r.status_code}")
    print(f"  Headers: {json.dumps(dict(r.headers))}")
    print(f"  Content ({len(r.content)} bytes): {repr(r.content)}")
    print(f"  Cookies: {r.cookies.get_dict()}")
    print("-" * 50)
