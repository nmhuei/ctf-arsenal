#!/usr/bin/env python3
"""
Solution for: sinkhole (Pwn - Browser/V8 JIT)
CSCV 2026 Quals

Vulnerability: MaglevSmiCheckElimination unsafe untag overwrite
Exploit delivery: Serves exploit.html over HTTP and submits URL to the bot.
"""
import argparse
import os
import socket
import subprocess
import sys
import time

DEFAULT_HOST = '113.20.103.216'
DEFAULT_PORT = 31337

def parse_args():
    parser = argparse.ArgumentParser(description="sinkhole exploit runner")
    parser.add_argument('--remote', default=f"{DEFAULT_HOST}:{DEFAULT_PORT}", help="Remote challenge host:port")
    parser.add_argument('--url', help="Publicly accessible URL to exploit.html (e.g. from ngrok/localhost.run)")
    return parser.parse_args()

def solve(options):
    if not options.url:
        print("[*] To trigger the bot, provide an accessible URL using --url <http://host:port/exploit.html>")
        print("[*] Or run the automated tunnel runner: bash 'solver/solve (2)/solve/remote.sh'")
        return

    host, port = options.remote.rsplit(':', 1)
    port = int(port)
    print(f"[*] Connecting to challenge bot at {host}:{port} ...")
    s = socket.create_connection((host, port), timeout=30)
    s.settimeout(90)

    buf = b""
    while b"URL to visit" not in buf:
        chunk = s.recv(4096)
        if not chunk:
            break
        buf += chunk
    print(f"[*] Prompt received: {buf.decode(errors='replace').strip()}")

    print(f"[*] Submitting target URL: {options.url}")
    s.sendall((options.url.strip() + "\n").encode())

    t0 = time.time()
    while time.time() - t0 < 80:
        chunk = s.recv(4096)
        if not chunk:
            break
        sys.stdout.write(chunk.decode(errors='replace'))
        sys.stdout.flush()
    s.close()

if __name__ == '__main__':
    solve(parse_args())
