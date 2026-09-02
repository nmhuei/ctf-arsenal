#!/usr/bin/env python3
from pwn import *
import subprocess
import hashlib
import base64

HOST = "mikuprotect.chals.sekai.team"
PORT = 1337

context.log_level = 'info'

def solve_pow(challenge):
    result = subprocess.run(
        challenge,
        shell=True,
        capture_output=True,
        text=True,
        timeout=120
    )
    return result.stdout.strip()

r = remote(HOST, PORT)

# PoW
r.recvuntil(b'solution: ')
pow_cmd = r.recvline().decode().strip()
print(f"PoW cmd: {pow_cmd[:80]}...")
sol = solve_pow(pow_cmd)
print(f"Pow solved: {sol[:40]}...")
r.sendline(sol.encode())

# Read protocol using recvuntil patterns
# sample_size
line = r.recvline().decode().strip()
print(f"1: {line}")

# sample_sha256
line = r.recvline().decode().strip()
print(f"2: {line}")
sha256_val = line.split('=')[1]

# sample_raw: header
line = r.recvline().decode().strip()
print(f"3: {line}")

# Now read sample_raw binary data - it comes as ascii hex dump?
# Read until we hit a non-hex line (target or prompt)
sample_data = b""
while True:
    chunk = r.recv(8192, timeout=3)
    if not chunk:
        break
    sample_data += chunk
    # Look for text markers in the stream
    try:
        text = chunk.decode('ascii', errors='replace')
        if 'target' in text or 'output' in text or 'print' in text or 'send' in text:
            print(f"Found marker in chunk: {text[:200]}")
    except:
        pass
    if len(sample_data) > 2543000:
        break

# Save sample
with open('/tmp/sample.exe', 'wb') as f:
    f.write(sample_data)

print(f"\nSample size: {len(sample_data)}")
# Verify sha256
actual_sha = hashlib.sha256(sample_data).hexdigest()
print(f"Expected SHA256: {sha256_val}")
print(f"Actual SHA256:   {actual_sha}")
print(f"Match: {actual_sha == sha256_val}")

# Now try to see what comes after
print(f"\nLast 200 bytes received: {sample_data[-200:]}")
print(f"\nTrying to read more...")

try:
    more = r.recv(4096, timeout=5)
    print(f"\nMore data ({len(more)} bytes): {more}")
except:
    print("No more data (timeout)")

r.close()
