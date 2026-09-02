import requests
import statistics
import time
import math
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
            dt = (time.perf_counter() - t0) * 1000  # ms
            if r.status_code == 502:
                time.sleep(3.5)
                continue
            return dt, r.status_code
        except Exception as e:
            time.sleep(3.5)

# Test 4 distinct characters: 'a', '0', 'A', 'Z'
# Perform 12 interleaved rounds so network conditions affect all characters equally
test_chars = ['a', '0', 'A', 'Z']
rounds = 10
results = {c: [] for c in test_chars}

print("=== BẮT ĐẦU KIỂM ĐỊNH THỐNG KÊ XÁC THỰC KÊNH THỜI GIAN (A/B TESTING) ===")
print(f"Đối tượng so sánh: {test_chars}")
print(f"Số vòng kiểm thử xen kẽ (Interleaved rounds): {rounds}")
print("Đang tiến hành đo đạc...\n")

for r in range(rounds):
    print(f"--- Vòng {r+1}/{rounds} ---")
    for c in test_chars:
        token = c + "0" * 47
        dt, status = query(token, delay=3.0)
        results[c].append(dt)
        print(f"  Char '{c}': {dt:.2f} ms (Status: {status})")

print("\n" + "="*50)
print("=== PHÂN TÍCH THỐNG KÊ TOÁN HỌC (STATISTICAL ANALYSIS) ===")
print("="*50)

def stats_summary(data):
    n = len(data)
    mean = statistics.mean(data)
    med = statistics.median(data)
    stdev = statistics.stdev(data) if n > 1 else 0
    # 95% Confidence Interval: Mean ± 1.96 * (stdev / sqrt(n))
    ci95 = 1.96 * (stdev / math.sqrt(n)) if n > 1 else 0
    return mean, med, stdev, ci95

for c in test_chars:
    mean, med, stdev, ci95 = stats_summary(results[c])
    print(f"Ký tự '{c}':")
    print(f"  - Mẫu đo (n={len(results[c])}): {[round(x,1) for x in results[c]]}")
    print(f"  - Trung bình (Mean): {mean:.2f} ms (±{stdev:.2f} ms)")
    print(f"  - Trung vị (Median): {med:.2f} ms")
    print(f"  - Khoảng tin cậy 95% (95% CI): [{mean - ci95:.2f} ms , {mean + ci95:.2f} ms]\n")

# Welch's t-test comparison between the highest mean and lowest mean
sorted_chars = sorted(test_chars, key=lambda c: statistics.mean(results[c]), reverse=True)
c_high = sorted_chars[0]
c_low = sorted_chars[-1]

mean1, _, s1, _ = stats_summary(results[c_high])
mean2, _, s2, _ = stats_summary(results[c_low])
n1, n2 = len(results[c_high]), len(results[c_low])

# t-score formula
se_diff = math.sqrt((s1**2 / n1) + (s2**2 / n2)) if (s1+s2) > 0 else 1
t_score = (mean1 - mean2) / se_diff if se_diff > 0 else 0

print(f"So sánh giữa ký tự cao nhất ('{c_high}') và thấp nhất ('{c_low}'):")
print(f"  - Chênh lệch Mean: {mean1 - mean2:.2f} ms")
print(f"  - t-Score: {t_score:.2f}")

if abs(t_score) < 2.0:
    print("  => KẾT LUẬN THỐNG KÊ: Không có sự khác biệt có ý nghĩa thống kê (p > 0.05).")
    print("     Mọi biến thiên thời gian hoàn toàn là do nhiễu mạng ngẫu nhiên (Network Jitter).")
else:
    print("  => KẾT LUẬN THỐNG KÊ: Có sự chênh lệch có ý nghĩa thống kê (p < 0.05).")
