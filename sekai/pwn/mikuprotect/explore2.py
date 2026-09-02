#!/usr/bin/env python3
from pwn import *
import subprocess
import hashlib
import struct

HOST = "mikuprotect.chals.sekai.team"
PORT = 1337

context.log_level = 'info'

def solve_pow(challenge):
    result = subprocess.run(challenge, shell=True, capture_output=True, text=True, timeout=120)
    return result.stdout.strip()

r = remote(HOST, PORT)

# PoW
r.recvuntil(b'solution: ')
pow_cmd = r.recvline().decode().strip()
print(f"PoW: {pow_cmd[:60]}...")
sol = solve_pow(pow_cmd)
print(f"Solved ({len(sol)} chars)")
r.sendline(sol.encode())

# Read metadata
r.recvuntil(b'sample_size=')
size_str = r.recvuntil(b'\n', drop=True).decode()
sample_size = int(size_str)
print(f"Sample size: {sample_size}")
assert sample_size < 10_000_000, f"Sample too big: {sample_size}"

r.recvuntil(b'sample_sha256=')
expected_sha = r.recvuntil(b'\n', drop=True).decode()
print(f"Expected SHA256: {expected_sha}")

r.recvuntil(b'sample_raw:\n')
print("Reading sample binary...")
sample = r.recv(sample_size, timeout=30)
print(f"Read {len(sample)} bytes")

actual_sha = hashlib.sha256(sample).hexdigest()
print(f"SHA256 match: {actual_sha == expected_sha}")

with open('/tmp/sample.exe', 'wb') as f:
    f.write(sample)
print("Saved to /tmp/sample.exe")

# Read any remaining data
print("\nChecking for more data...")
try:
    rest = r.recv(4096, timeout=5)
    print(f"Extra data ({len(rest)} bytes):")
    print(repr(rest[:500]))
except:
    print("No extra data")

# Maybe server is now waiting for us to send a patched binary?
print("\nTrying to send probe...")
r.send(b"test\n")
try:
    resp = r.recv(4096, timeout=5)
    print(f"Response: {resp}")
except:
    print("No response")

r.close()
