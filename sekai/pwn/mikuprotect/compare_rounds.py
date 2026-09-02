#!/usr/bin/env python3
"""Download 2 samples (different targets), find what bytes change between them."""
from pwn import *
import subprocess, hashlib, struct, time

HOST = "mikuprotect.chals.sekai.team"
PORT = 1337
context.log_level = 'warn'

def solve_pow(challenge):
    result = subprocess.run(challenge, shell=True, capture_output=True, text=True, timeout=120)
    return result.stdout.strip()

def download():
    r = remote(HOST, PORT)
    r.recvuntil(b'proof of work:\n')
    pow_cmd = r.recvuntil(b'\nsolution: ', drop=True).decode().strip()
    sol = solve_pow(pow_cmd)
    r.sendline(sol.encode())
    r.recvuntil(b'sample_size=')
    sample_size = int(r.recvuntil(b'\n', drop=True).decode())
    r.recvuntil(b'sample_sha256=')
    expected_sha = r.recvuntil(b'\n', drop=True).decode()
    r.recvuntil(b'sample_raw:\n')
    sample = b""
    while len(sample) < sample_size:
        chunk = r.recv(min(65536, sample_size - len(sample)), timeout=30)
        if not chunk: break
        sample += chunk
    time.sleep(0.5)
    rest = b""
    while True:
        try:
            c = r.recv(4096, timeout=5)
            if not c: break
            rest += c
        except: break
    r.close()
    return sample, rest.decode('ascii', errors='replace')

# Download sample 1
print("Downloading sample 1...")
s1, p1 = download()
print(f"S1: {len(s1)} bytes")
print(f"P1: {p1.strip()}")

# Parse target and rotors from p1
import re
m1 = re.search(r"target=b'([^']*)'", p1)
t1 = m1.group(1) if m1 else ""
m1 = re.search(r'rotors? a=0x([0-9a-fA-F]+) b=0x([0-9a-fA-F]+) c=0x([0-9a-fA-F]+) d=0x([0-9a-fA-F]+)', p1)
r1 = [int(m1.group(i), 16) for i in range(1,5)] if m1 else []
print(f"Target1: {repr(t1)}")
print(f"Rotors1: {[hex(v) for v in r1]}")

# Download sample 2
print("\nDownloading sample 2...")
s2, p2 = download()
print(f"S2: {len(s2)} bytes")
print(f"P2: {p2.strip()}")

m2 = re.search(r"target=b'([^']*)'", p2)
t2 = m2.group(1) if m2 else ""
m2 = re.search(r'rotors? a=0x([0-9a-fA-F]+) b=0x([0-9a-fA-F]+) c=0x([0-9a-fA-F]+) d=0x([0-9a-fA-F]+)', p2)
r2 = [int(m2.group(i), 16) for i in range(1,5)] if m2 else []
print(f"Target2: {repr(t2)}")
print(f"Rotors2: {[hex(v) for v in r2]}")

# Compare sections
sections = [
    ("PE hdr", 0, 0x400),
    (".text", 0x400, 0x2000),
    (".rdata", 0x2400, 0xe00),
    (".data", 0x3200, 0x200),
    (".pdata", 0x3400, 0x400),
    (".6%l", 0x3800, 0x266e00),
    (".reloc", 0x26a600, 0x200),
]

print(f"\n{'='*60}")
print("Section-by-section comparison:")
print(f"{'='*60}")

for name, soff, size in sections:
    max_size = min(len(s1) - soff, len(s2) - soff, size)
    sec1 = s1[soff:soff+max_size]
    sec2 = s2[soff:soff+max_size]

    diffs = [(i, sec1[i], sec2[i]) for i in range(len(sec1)) if sec1[i] != sec2[i]]
    print(f"\n{name:12s}: {len(diffs):6d} diff bytes / {len(sec1)}")

    # If small number of diffs, show them
    if 1 <= len(diffs) <= 64:
        for off, oldv, newv in diffs:
            print(f"  +0x{off:x}: 0x{oldv:02x} -> 0x{newv:02x}")

    # Check for 4 DWORD patterns in diffs
    if len(diffs) >= 16:
        # Group consecutive diffs
        groups = []
        if diffs:
            start = diffs[0][0]
            prev = start
            for off, oldv, newv in diffs[1:]:
                if off != prev + 1:
                    groups.append((start, prev))
                    start = off
                prev = off
            groups.append((start, prev))

        for gs, ge in groups:
            gsz = ge - gs + 1
            if gsz == 16:
                old = bytes(s1[soff+gs:soff+ge+1])
                new = bytes(s2[soff+gs:soff+ge+1])
                old_dwords = struct.unpack('<IIII', old)
                new_dwords = struct.unpack('<IIII', new)
                print(f"  16-byte change at +0x{gs:x}:")
                print(f"    Old: {[hex(v) for v in old_dwords]}")
                print(f"    New: {[hex(v) for v in new_dwords]}")
PYEOF
