#!/usr/bin/env python3
"""Test if X-Forwarded-For (and friends) bypass the 502 limiter."""
import random
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io/api/authenticate"

print("quiet 70s to refill...", flush=True)
time.sleep(70)


def rand_ip():
    return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


s = requests.Session()
s.verify = False

print("=== control: 6 fast requests, no XFF ===", flush=True)
for i in range(6):
    r = s.post(URL, json={"token": "0" * 48}, timeout=20)
    print(f"  {i+1}: {r.status_code}", flush=True)
    time.sleep(0.5)

print("=== test: 10 fast requests, random XFF per request ===", flush=True)
ok = bad = 0
for i in range(10):
    h = {"X-Forwarded-For": rand_ip(), "X-Real-IP": None}
    r = s.post(URL, json={"token": "0" * 48}, headers=h, timeout=20)
    if r.status_code == 401:
        ok += 1
    else:
        bad += 1
    print(f"  {i+1}: {r.status_code} xff={h['X-Forwarded-For']}", flush=True)
    time.sleep(0.5)
print(f"XFF result: {ok} ok / {bad} bad")
