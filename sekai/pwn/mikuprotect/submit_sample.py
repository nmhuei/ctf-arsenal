#!/usr/bin/env python3
from pwn import *
import subprocess
import hashlib
import time
import sys

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
log.info(f"PoW: {pow_cmd[:60]}...")
sol = solve_pow(pow_cmd)
log.info(f"Solved")
r.sendline(sol.encode())

# Metadata
r.recvuntil(b'sample_size=')
sample_size = int(r.recvuntil(b'\n', drop=True).decode())
r.recvuntil(b'sample_sha256=')
expected_sha = r.recvuntil(b'\n', drop=True).decode()

r.recvuntil(b'sample_raw:\n')
sample = b""
while len(sample) < sample_size:
    chunk = r.recv(min(65536, sample_size - len(sample)), timeout=30)
    if not chunk:
        break
    sample += chunk

actual_sha = hashlib.sha256(sample).hexdigest()
assert actual_sha == expected_sha, "SHA256 mismatch"
log.info(f"Downloaded {len(sample)} bytes")

# Read prompt
time.sleep(1)
prompt = b""
while True:
    try:
        chunk = r.recv(4096, timeout=5)
        if not chunk: break
        prompt += chunk
    except: break

log.info(f"Prompt:\n{prompt.decode('ascii', errors='replace')}")

# Send the ORIGINAL binary back unpatched to see error
log.info("Sending original binary back (unpatched)...")
r.send(sample)

time.sleep(3)
try:
    resp = r.recv(4096, timeout=10)
    log.info(f"Response: {resp.decode('ascii', errors='replace')}")
except:
    log.warning("No immediate response")
    try:
        resp = r.recv(4096, timeout=30)
        log.info(f"Response (30s): {resp.decode('ascii', errors='replace')}")
    except:
        log.error("No response after 30s")

r.close()
