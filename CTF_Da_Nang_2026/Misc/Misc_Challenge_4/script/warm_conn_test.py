#!/usr/bin/env python3
"""Verify: warm keep-alive connection allows fast sequential requests."""
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io/api/authenticate"

print("quiet period 75s ...", flush=True)
time.sleep(75)

s = requests.Session()
s.verify = False

# warm-up
r = s.post(URL, json={"token": "0" * 48}, timeout=25)
print(f"warmup: {r.status_code}", flush=True)
if r.status_code == 502:
    print("still limited; abort", flush=True)
    raise SystemExit(1)

# rapid fire on same session
ok = bad = 0
for i in range(12):
    t0 = time.perf_counter()
    r = s.post(URL, json={"token": f"{i%10}" * 48}, timeout=25)
    dt = (time.perf_counter() - t0) * 1000
    mark = "OK " if r.status_code == 401 else "BAD"
    if r.status_code == 401:
        ok += 1
    else:
        bad += 1
    print(f"{i+1:2d}: {r.status_code} {dt:.0f}ms [{mark}] conn-id={id(s.get_adapter(URL))}", flush=True)
    time.sleep(1.2)

print(f"\nresult: {ok} ok / {bad} bad")
