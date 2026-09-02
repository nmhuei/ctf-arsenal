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

# PoW
r.recvuntil(b'proof of work:\n')
pow_cmd = r.recvuntil(b'\nsolution: ', drop=True).decode().strip()
print(f"PoW cmd: {pow_cmd[:60]}...")
sol = solve_pow(pow_cmd)
print(f"Solved ({len(sol)} chars)")
r.sendline(sol.encode())

# Metadata
r.recvuntil(b'sample_size=')
sample_size = int(r.recvuntil(b'\n', drop=True).decode())
print(f"Sample size: {sample_size}")

r.recvuntil(b'sample_sha256=')
expected_sha = r.recvuntil(b'\n', drop=True).decode()
print(f"Expected SHA256: {expected_sha}")

r.recvuntil(b'sample_raw:\n')

# Read all sample bytes properly
sample = b""
while len(sample) < sample_size:
    chunk = r.recv(min(65536, sample_size - len(sample)), timeout=30)
    if not chunk:
        break
    sample += chunk
    if len(sample) % 262144 == 0:
        print(f"  Read {len(sample)}/{sample_size} bytes...")

print(f"Read {len(sample)} bytes total")
actual_sha = hashlib.sha256(sample).hexdigest()
print(f"SHA256 match: {actual_sha == expected_sha}")

with open('/tmp/sample.exe', 'wb') as f:
    f.write(sample)
print("Saved to /tmp/sample.exe")

# Read post-sample data
print("\nReading post-sample data...")
time.sleep(0.5)
post_data = b""
while True:
    try:
        chunk = r.recv(4096, timeout=5)
        if not chunk:
            break
        post_data += chunk
        print(f"Got {len(chunk)} bytes post-sample")
    except:
        break

if post_data:
    print(f"\nPost-sample data ({len(post_data)} bytes):")
    print(repr(post_data[:1000]))
else:
    print("No post-sample data - server might be waiting for input")
    r.send(b"test\n")
    try:
        resp = r.recv(4096, timeout=5)
        print(f"Response: {resp}")
    except:
        print("No response")

r.close()
