#!/usr/bin/env python3
import socket
import subprocess
import sys
import re
import os
import struct
import hashlib
import base64

HOST = "mikuprotect.chals.sekai.team"
PORT = 1337

def solve_pow(challenge):
    """Solve proof of work using the provided command"""
    result = subprocess.run(
        challenge,
        shell=True,
        capture_output=True,
        text=True,
        timeout=60
    )
    return result.stdout.strip()

def recv_until(sock, marker):
    data = b""
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data.decode(errors='replace')

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((HOST, PORT))

    # Receive initial prompt
    banner = recv_until(sock, b"solution: ")
    print("=== BANNER ===")
    print(banner)

    # Parse PoW command
    lines = banner.strip().split("\n")
    pow_cmd = None
    for line in lines:
        if "curl" in line or "sh" in line:
            pow_cmd = line.strip()

    if pow_cmd:
        print(f"\n=== PoW CMD ===\n{pow_cmd}")
        solution = solve_pow(pow_cmd)
        print(f"=== SOLUTION ===\n{solution}")
        sock.sendall((solution + "\n").encode())

    # Receive response
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            print(data.decode(errors='replace'), end='')
        except socket.timeout:
            break

    sock.close()

if __name__ == "__main__":
    main()
