#!/usr/bin/env python3
"""
Download one sample, save it, then compare with the earlier sample
to find the rotor storage offset.
"""
from pwn import *
import subprocess
import hashlib
import struct
import time

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
    actual_sha = hashlib.sha256(sample).hexdigest()
    assert actual_sha == expected_sha
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

print("Downloading sample...")
sample, prompt = download()
print(f"Sample: {len(sample)} bytes, SHA256: {hashlib.sha256(sample).hexdigest()}")
print(f"Prompt: {prompt}")

# Save
with open('/tmp/sample2.exe', 'wb') as f:
    f.write(sample)

# Compare with old sample if it exists
try:
    with open('/tmp/sample.exe', 'rb') as f:
        old = f.read()

    if len(old) == len(sample):
        diffs = []
        for i in range(len(old)):
            if old[i] != sample[i]:
                diffs.append(i)

        print(f"\nDiffs with old sample: {len(diffs)} bytes")

        if diffs:
            groups = []
            start = diffs[0]
            prev = start
            for pos in diffs[1:]:
                if pos != prev + 1:
                    groups.append((start, prev))
                    start = pos
                prev = pos
            groups.append((start, prev))

            for s, e in groups:
                sz = e - s + 1
                print(f"  0x{s:08x}-0x{e:08x} ({sz} bytes)")
                print(f"    Old: {old[s:e+1][:64].hex()}")
                print(f"    New: {sample[s:e+1][:64].hex()}")
                # Check section
                for sec, soff, ssz in [('.text',0x400,0x2000),('.rdata',0x2400,0xe00),
                    ('.data',0x3200,0x200),('.pdata',0x3400,0x400),
                    ('.6%l',0x3800,0x266e00),('.reloc',0x26a600,0x200)]:
                    if soff <= s and s+sz <= soff+ssz:
                        print(f"    Section: {sec}")
    else:
        print(f"\nDifferent sizes: {len(old)} vs {len(sample)}")
        min_len = min(len(old), len(sample))
        diffs = [i for i in range(min_len) if old[i] != sample[i]]
        print(f"Diffs: {len(diffs)}")
        if diffs:
            for d in diffs[:20]:
                print(f"  0x{d:08x}: old=0x{old[d]:02x} new=0x{sample[d]:02x}")
except FileNotFoundError:
    print("No old sample to compare with")
