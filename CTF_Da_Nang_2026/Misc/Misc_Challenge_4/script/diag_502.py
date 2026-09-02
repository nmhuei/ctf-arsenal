#!/usr/bin/env python3
"""Diagnose the 502 behavior: which layer, headers, per-conn vs global limit."""
import time
import threading
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io/api/authenticate"


def one(tag, session=None, quiet=25):
    s = session or requests.Session()
    s.verify = False
    time.sleep(quiet)
    t0 = time.perf_counter()
    r = s.post(URL, json={"token": "0" * 48}, timeout=25)
    dt = (time.perf_counter() - t0) * 1000
    print(f"[{tag}] {r.status_code} {dt:.0f}ms")
    if r.status_code == 502:
        for k, v in r.headers.items():
            print(f"    {k}: {v}")
        print(f"    body[:300]: {r.text[:300]!r}")
    else:
        print(f"    server={r.headers.get('server')} body[:80]={r.text[:80]!r}")
    return r


print("=== A) single request, inspect 502 shape ===")
one("A1", quiet=5)

print("\n=== B) two fresh connections fired simultaneously ===")
results = {}
def worker(i):
    s = requests.Session(); s.verify = False
    t0 = time.perf_counter()
    try:
        r = s.post(URL, json={"token": "0" * 48}, timeout=25)
        results[i] = (r.status_code, (time.perf_counter()-t0)*1000)
    except Exception as e:
        results[i] = ("err:" + type(e).__name__, -1)

# quiet period first so bucket is full
time.sleep(30)
threads = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
for t in threads: t.start()
for t in threads: t.join()
for i in sorted(results):
    print(f"  conn{i}: {results[i]}")

print("\n=== C) same two connections, another simultaneous pair after cooldown ===")
time.sleep(40)
s1 = requests.Session(); s1.verify = False
s2 = requests.Session(); s2.verify = False
res2 = {}
def w2(idx, s):
    t0 = time.perf_counter()
    try:
        r = s.post(URL, json={"token": "0"*48}, timeout=25)
        res2[idx] = (r.status_code, round((time.perf_counter()-t0)*1000))
    except Exception as e:
        res2[idx] = ("err:"+type(e).__name__, -1)
t1 = threading.Thread(target=w2, args=(1, s1))
t2 = threading.Thread(target=w2, args=(2, s2))
t1.start(); t2.start(); t1.join(); t2.join()
print(" ", res2)
