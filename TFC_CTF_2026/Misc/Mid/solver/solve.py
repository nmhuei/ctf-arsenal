#!/usr/bin/env python3
"""Solver for TFC CTF 2026 - Misc / Mid (pwntools version)

Binary search with burn-16 strategy.
Remote servers use pty echo → after sendline, data arrives as:
  echo\r\nresponse\r\n> 
We recvuntil("> ") to get everything, then parse the last meaningful line.
"""
import argparse
import re
import string
import time
from pathlib import Path

from pwn import context, log, remote, process

PASSWORD_LENGTH = 30
MAX_QUERIES = 195
ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase
TOTAL = 62**PASSWORD_LENGTH
FLAG_RE = re.compile(r"(?:TFCCTF|TEST)\{[^}\r\n]+\}")


def num_to_str(num: int) -> str:
    chars = []
    for _ in range(PASSWORD_LENGTH):
        chars.append(ALPHABET[num % 62])
        num //= 62
    return "".join(reversed(chars))


def send_query(io, query: str, is_remote: bool) -> str:
    """Send a query and return the server's response line."""
    io.sendline(query.encode())
    if is_remote:
        # Remote pty: data = "echo\r\nresponse\r\n> "
        raw = io.recvuntil(b"> ", timeout=15)
        # Split lines, filter out echo and empty
        lines = raw.decode(errors="replace").replace("\r", "").strip().split("\n")
        # Last non-empty line before "> " is the response
        for line in reversed(lines):
            line = line.strip().rstrip(">").strip()
            if line and line != query:
                return line
        return ""
    else:
        # Local subprocess: no echo, just "response\n> "
        raw = io.recvuntil(b"> ", timeout=5)
        lines = raw.decode(errors="replace").replace("\r", "").strip().split("\n")
        for line in reversed(lines):
            line = line.strip().rstrip(">").strip()
            if line:
                return line
        return ""


def attempt_solve(io, is_remote: bool) -> str | None:
    # Read banner + first prompt
    io.recvuntil(b"> ", timeout=15)

    # Phase 1: Burn 16 queries with state=1
    for i in range(16):
        resp = send_query(io, "1 0", is_remote)
        # Don't care about response in burn phase

    # Phase 2: Binary search
    L = 0
    R = TOTAL - 1

    for q in range(16, MAX_QUERIES):
        mid_val = (L + R) // 2
        guess = num_to_str(mid_val)
        resp = send_query(io, f"1 {guess}", is_remote)

        # Check for flag
        flag_match = FLAG_RE.search(resp)
        if flag_match:
            return flag_match.group()

        if "equal" in resp:
            # Flag should be on next output - but send_query already consumed up to "> "
            # Try reading one more line
            try:
                extra = io.recvline(timeout=5).decode(errors="replace").strip()
                flag_match = FLAG_RE.search(extra)
                if flag_match:
                    return flag_match.group()
                return extra
            except Exception:
                return resp

        if "smaller" in resp:
            L = mid_val + 1
        elif "larger" in resp:
            R = mid_val - 1
        else:
            log.warning("unexpected response: %r", resp)
            return None

    return None


def solve():
    parser = argparse.ArgumentParser(description="Solver for TFC CTF 2026 - Mid")
    parser.add_argument("--host", type=str, default=None, help="Remote host")
    parser.add_argument("-p", "--port", type=int, default=1337, help="Remote port")
    parser.add_argument("--plain", action="store_true", help="Plain TCP (no TLS)")
    parser.add_argument("--debug", action="store_true", help="pwntools DEBUG mode")
    parser.add_argument("--timeout", type=float, default=120.0, help="Connection timeout")
    args = parser.parse_args()

    if args.debug:
        context.log_level = "debug"
    else:
        context.log_level = "info"

    is_remote = args.host is not None
    chal_script = str(Path(__file__).resolve().parents[1] / "challenge" / "chall.py")

    if is_remote:
        log.info("Target: %s:%d (ssl=%s)", args.host, args.port, not args.plain)
    else:
        log.info("Target: local %s", chal_script)

    t0 = time.time()
    attempts = 0

    while True:
        attempts += 1
        io = None
        try:
            if is_remote:
                if attempts == 1 or attempts % 5 == 0:
                    log.info("Attempt %d ...", attempts)
                io = remote(args.host, args.port, ssl=not args.plain, timeout=args.timeout)
            else:
                io = process(["python3", "-u", chal_script])

            flag = attempt_solve(io, is_remote)
            if flag:
                elapsed = time.time() - t0
                log.success("SOLVED on attempt %d in %.2fs!", attempts, elapsed)
                log.success("FLAG: %s", flag)
                flag_file = Path(__file__).resolve().parents[1] / "flag.txt"
                flag_file.write_text(flag.strip() + "\n", encoding="utf-8")
                log.info("Written to %s", flag_file)
                return flag

        except (EOFError, OSError, TimeoutError) as exc:
            if attempts == 1 or attempts % 10 == 0:
                log.warning("Attempt %d failed (%s)", attempts, exc)
        finally:
            if io:
                io.close()

        if attempts % 10 == 0:
            log.info("Attempt %d ... still hunting switch_at <= 16", attempts)


if __name__ == "__main__":
    solve()
