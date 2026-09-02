import requests
import time
import urllib3
import statistics

urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io/api/authenticate"
session = requests.Session()
session.verify = False

def send_test(token, pause=3.0):
    time.sleep(pause)
    while True:
        try:
            t0 = time.perf_counter()
            r = session.post(BASE_URL, json={"token": token}, timeout=10)
            dt = (time.perf_counter() - t0) * 1000
            if r.status_code == 502:
                time.sleep(3.5)
                continue
            return dt, r.status_code, r.text
        except Exception as e:
            time.sleep(3.5)

print("=== 1. KIỂM TRA ĐỘ DÀI TOKEN ===")
for length in [0, 10, 47, 48, 49]:
    tok = "a" * length
    dt, status, text = send_test(tok)
    print(f"Length {length:2d}: Status={status}, Response={text.strip()}, Time={dt:.2f}ms")

print("\n=== 2. KIỂM TRA KÝ TỰ ĐẶC BIỆT TRONG TOKEN 48 KÝ TỰ ===")
test_tokens = {
    "all_digits": "0" * 48,
    "all_lowercase": "a" * 48,
    "all_uppercase": "A" * 48,
    "has_special_char": "a" * 47 + "!",
    "has_space": "a" * 47 + " ",
    "has_null_byte": "a" * 47 + "\x00",
}
for name, tok in test_tokens.items():
    dt, status, text = send_test(tok)
    print(f"{name:18s}: Status={status}, Response={text.strip()}")

print("\n=== 3. KIỂM TRA ĐO THỜI GIAN (10 MẪU LẶP CHO CÙNG 1 TOKEN) ===")
tok = "0" * 48
times = []
for i in range(10):
    dt, status, _ = send_test(tok)
    times.append(dt)
print(f"Token: '0'*48 | 10 lần đo: {[round(t, 2) for t in times]}")
print(f"Min: {min(times):.2f}ms | Med: {statistics.median(times):.2f}ms | Max: {max(times):.2f}ms | Stdev: {statistics.stdev(times):.2f}ms")
