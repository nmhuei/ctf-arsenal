import requests
import time
import urllib3

urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

def test_delay(delay_sec, count=5):
    print(f"\nTesting delay {delay_sec}s ({count} requests):")
    statuses = []
    times = []
    for i in range(count):
        time.sleep(delay_sec)
        t0 = time.perf_counter()
        try:
            r = s.post(f"{BASE_URL}/api/authenticate", json={"token": "0"*48}, timeout=10)
            dt = (time.perf_counter() - t0) * 1000
            statuses.append(r.status_code)
            times.append(dt)
            print(f"  Req {i+1}: {r.status_code} ({dt:.1f}ms)")
        except Exception as e:
            statuses.append("err")
            print(f"  Req {i+1}: err ({e})")
    
    success_rate = sum(1 for st in statuses if st == 401) / count * 100
    print(f"Delay {delay_sec}s -> 401 rate: {success_rate:.0f}%")
    return success_rate

print("Calibrating safe request interval...")
for d in [0.5, 0.8, 1.0, 1.2, 1.5, 2.0]:
    rate = test_delay(d, 5)
    if rate == 100.0:
        print(f"\n=> 100% stable at delay = {d}s")
        # test once more to confirm
        rate2 = test_delay(d, 5)
        if rate2 == 100.0:
            print(f"Confirmed stable delay: {d}s")
            break
