#!/usr/bin/env python3
"""
Upload/run helper for the OmniCTF WinCapture TLS endpoint.

Examples:
  python3 send_wincapture.py exploit.exe --probe
  python3 send_wincapture.py exploit.exe --mode auto --attempts 50
  python3 send_wincapture.py exploit.exe --mode b64line
  python3 send_wincapture.py exploit.exe --mode b64size
  python3 send_wincapture.py exploit.exe --mode rawsize

The service banner determines the upload protocol. If auto mode cannot
recognize it, --probe prints the exact banner without sending the payload.
"""

from __future__ import annotations

import argparse
import base64
import re
import select
import socket
import ssl
import sys
import time
from pathlib import Path

DEFAULT_HOST = "wincapture-bcb34c2a8ddb.inst.omnictf.com"
DEFAULT_PORT = 1337
FLAG_RE = re.compile(rb"CTF\{[^}\r\n]{1,300}\}")


def tls_connect(host: str, port: int, timeout: float) -> ssl.SSLSocket:
    raw = socket.create_connection((host, port), timeout=timeout)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    wrapped = context.wrap_socket(raw, server_hostname=host)
    wrapped.setblocking(False)
    return wrapped


def recv_quiet(sock: ssl.SSLSocket, quiet: float, total: float) -> bytes:
    data = bytearray()
    start = time.monotonic()
    last = start

    while time.monotonic() - start < total:
        wait = max(0.0, min(0.25, total - (time.monotonic() - start)))
        readable, _, _ = select.select([sock], [], [], wait)
        if not readable:
            if data and time.monotonic() - last >= quiet:
                break
            continue

        try:
            chunk = sock.recv(65536)
        except (ssl.SSLWantReadError, BlockingIOError):
            continue

        if not chunk:
            break

        data.extend(chunk)
        last = time.monotonic()

    return bytes(data)


def send_all(sock: ssl.SSLSocket, data: bytes, timeout: float = 20.0) -> None:
    view = memoryview(data)
    deadline = time.monotonic() + timeout

    while view:
        if time.monotonic() >= deadline:
            raise TimeoutError("send timeout")

        _, writable, _ = select.select([], [sock], [], 0.25)
        if not writable:
            continue

        try:
            sent = sock.send(view)
        except (ssl.SSLWantWriteError, BlockingIOError):
            continue

        if sent <= 0:
            raise ConnectionError("connection closed while sending")
        view = view[sent:]


def choose_auto_mode(banner: bytes) -> str | None:
    lower = banner.lower()

    mentions_b64 = b"base64" in lower or b"b64" in lower
    mentions_size = any(word in lower for word in
                        (b"size", b"length", b"number of bytes", b"bytes:"))
    mentions_raw = any(word in lower for word in
                       (b"raw", b"binary", b"executable", b"exe"))

    if mentions_b64 and mentions_size:
        return "b64size"
    if mentions_b64:
        return "b64line"
    if mentions_size and mentions_raw:
        return "rawsize"
    return None


def upload_once(
    host: str,
    port: int,
    payload: bytes,
    mode: str,
    timeout: float,
    probe: bool,
) -> bytes:
    sock = tls_connect(host, port, timeout)
    try:
        banner = recv_quiet(sock, quiet=0.5, total=3.0)
        if banner:
            sys.stdout.buffer.write(banner)
            if not banner.endswith(b"\n"):
                print()
            sys.stdout.flush()

        if probe:
            return banner

        selected = mode
        if selected == "auto":
            selected = choose_auto_mode(banner)
            if selected is None:
                print(
                    "[-] Auto mode could not identify the upload protocol.\n"
                    "    Run with --probe, then choose --mode b64line, "
                    "b64size, rawsize or raw.",
                    file=sys.stderr,
                )
                return banner

        encoded = base64.b64encode(payload)

        if selected == "b64line":
            send_all(sock, encoded + b"\n")

        elif selected == "b64size":
            # Common CTF convention: encoded-character count, then one
            # base64 line. If the banner explicitly says decoded/raw size,
            # use --mode rawsize instead.
            send_all(sock, str(len(encoded)).encode() + b"\n")
            middle = recv_quiet(sock, quiet=0.25, total=1.5)
            if middle:
                sys.stdout.buffer.write(middle)
                sys.stdout.flush()
            send_all(sock, encoded + b"\n")

        elif selected == "rawsize":
            send_all(sock, str(len(payload)).encode() + b"\n")
            middle = recv_quiet(sock, quiet=0.25, total=1.5)
            if middle:
                sys.stdout.buffer.write(middle)
                sys.stdout.flush()
            send_all(sock, payload)

        elif selected == "raw":
            send_all(sock, payload)

        else:
            raise ValueError(f"unsupported mode: {selected}")

        output = banner + recv_quiet(sock, quiet=1.5, total=45.0)
        new_output = output[len(banner):]
        if new_output:
            sys.stdout.buffer.write(new_output)
            if not new_output.endswith(b"\n"):
                print()
            sys.stdout.flush()
        return output
    finally:
        try:
            sock.close()
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", nargs="?", type=Path, help="compiled exploit.exe")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument(
        "--mode",
        choices=("auto", "b64line", "b64size", "rawsize", "raw"),
        default="auto",
    )
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument(
        "--probe",
        action="store_true",
        help="only print the service banner; do not upload",
    )
    args = parser.parse_args()

    if args.probe:
        payload = b""
    else:
        if args.payload is None:
            parser.error("payload is required unless --probe is used")
        if not args.payload.is_file():
            parser.error(f"payload not found: {args.payload}")

        payload = args.payload.read_bytes()
        if not payload:
            parser.error("payload is empty")

    attempts = max(1, args.attempts)
    for attempt in range(1, attempts + 1):
        print(f"[*] Connection attempt {attempt}/{attempts}")
        try:
            output = upload_once(
                args.host,
                args.port,
                payload,
                args.mode,
                args.timeout,
                args.probe,
            )
        except (OSError, ssl.SSLError, TimeoutError, ConnectionError) as exc:
            print(f"[-] Connection failed: {exc}", file=sys.stderr)
            output = b""

        match = FLAG_RE.search(output)
        if match:
            print(f"[+] Flag found: {match.group().decode(errors='replace')}")
            return 0

        if args.probe:
            return 0

        if attempt != attempts:
            time.sleep(max(0.0, args.delay))

    print("[-] No flag found.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
