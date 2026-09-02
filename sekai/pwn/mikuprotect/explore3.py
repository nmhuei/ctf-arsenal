#!/usr/bin/env python3
from pwn import *
import subprocess
import hashlib

HOST = "mikuprotect.chals.sekai.team"
PORT = 1337

context.log_level = 'info'

def solve_pow(challenge):
    result = subprocess.run(challenge, shell=True, capture_output=True, text=True, timeout=120)
    return result.stdout.strip()

r = remote(HOST, PORT)

# Read PoW: "proof of work:\ncurl ...\nsolution: "
r.recvuntil(b'proof of work:\n')
pow_cmd = r.recvuntil(b'\nsolution: ', drop=True).decode().strip()
print(f"PoW cmd: {pow_cmd[:60]}...")

sol = solve_pow(pow_cmd)
print(f"Solved ({len(sol)} chars): {sol[:40]}...")
r.sendline(sol.encode())

# Read metadata
r.recvuntil(b'sample_size=')
size_str = r.recvuntil(b'\n', drop=True).decode()
sample_size = int(size_str)
print(f"Sample size: {sample_size}")

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

# Read what comes after the binary (target string)
print("\nReading post-sample data...")
try:
    post = r.recvuntil(b'\n', timeout=10)
    print(f"Post-sample line: {post}")
except:
    print("No line after sample")
    try:
        post = r.recv(4096, timeout=5)
        print(f"Raw post (no line): {post[:200]}")
    except:
        print("No post data at all")

r.close()
