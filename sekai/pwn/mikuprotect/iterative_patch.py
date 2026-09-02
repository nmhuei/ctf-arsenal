#!/usr/bin/env python3
"""
Smart approach:
1. Download sample
2. Find all .text calls into .6%l
3. For each call target, try patching 4 rotor DWORDs at various offsets relative to that target
4. Try each patch against server
"""
from pwn import *
import subprocess, hashlib, struct, time, re

HOST = "mikuprotect.chals.sekai.team"
PORT = 1337
context.log_level = 'info'

def solve_pow(challenge):
    result = subprocess.run(challenge, shell=True, capture_output=True, text=True, timeout=120)
    return result.stdout.strip()

def demo_one():
    """Download sample and try different patch locations"""
    r = remote(HOST, PORT)

    # PoW
    r.recvuntil(b'proof of work:\n')
    pow_cmd = r.recvuntil(b'\nsolution: ', drop=True).decode().strip()
    log.info(f"PoW: {pow_cmd[:60]}...")
    sol = solve_pow(pow_cmd)
    r.sendline(sol.encode())

    # Metadata
    r.recvuntil(b'sample_size=')
    sample_size = int(r.recvuntil(b'\n', drop=True).decode())
    r.recvuntil(b'sample_sha256=')
    expected_sha = r.recvuntil(b'\n', drop=True).decode()
    r.recvuntil(b'sample_raw:\n')

    # Binary
    sample = b""
    while len(sample) < sample_size:
        chunk = r.recv(min(65536, sample_size - len(sample)), timeout=30)
        if not chunk: break
        sample += chunk

    # Parse prompt
    time.sleep(0.5)
    rest = b""
    while True:
        try:
            c = r.recv(4096, timeout=5)
            if not c: break
            rest += c
        except: break

    prompt = rest.decode('ascii', errors='replace')
    m = re.search(r"target=b'([^']*)'", prompt)
    target_str = m.group(1) if m else ""
    m = re.search(r'rotors? a=0x([0-9a-fA-F]+) b=0x([0-9a-fA-F]+) c=0x([0-9a-fA-F]+) d=0x([0-9a-fA-F]+)', prompt)
    rotors = [int(m.group(i), 16) for i in range(1,5)] if m else []

    log.info(f"Target: {repr(target_str)}")
    log.info(f"Rotors: {[hex(v) for v in rotors]}")
    log.info(f"Sample: {len(sample)} bytes, SHA256: {hashlib.sha256(sample).hexdigest()}")

    return r, sample, target_str, rotors, prompt

def get_6pct_l_entries(text):
    """Find calls into .6%l section from .text"""
    calls = []
    for i in range(len(text) - 5):
        # e8 XX XX XX XX = call rel32
        if text[i] == 0xe8:
            off = struct.unpack('<i', text[i+1:i+5])[0]
            target = 0x140001000 + i + 5 + off  # VA
            if 0x140006000 <= target <= 0x140267000:
                calls.append((i, target, target - 0x140006000, 'call'))
    return calls

def try_patch(r, sample, rotors, offset, label):
    """Patch 4 rotor DWORDs at given offset and submit"""
    d = bytearray(sample)
    for j, rotor in enumerate(rotors):
        struct.pack_into('<I', d, offset + j*4, rotor)

    log.info(f"Sending [{label}] (offset=0x{offset:x})")
    r.send(bytes(d))
    time.sleep(3)
    try:
        resp = r.recv(4096, timeout=10)
        return resp.decode('ascii', errors='replace').strip()
    except:
        return "timeout"

def main():
    r, sample, target_str, rotors, prompt = demo_one()

    text = sample[0x400:0x400+0x2000]

    # Find all calls into .6%l
    calls = get_6pct_l_entries(text)
    log.info(f"Found {len(calls)} calls into .6%l")
    for off_va, target_va, target_rva, call_type in calls[:10]:
        log.info(f"  .text+0x{off_va:x}: call .6%l+0x{target_rva:x}")

    # The main function entry - try various offsets
    # For each call target, try patching rotors at +0, +8, +16, +32 from target
    offsets_to_try = []

    for off_va, target_va, target_rva, call_type in calls:
        # offset within .6%l section
        file_off = 0x3800 + target_rva
        # Try various sub-offsets from the pcode entry
        for sub in [0, 4, 8, 12, 16, 20, 24, 28, 32, 64, 128, 256, 512]:
            candidate = file_off + sub
            if candidate + 16 <= len(sample):
                offsets_to_try.append((candidate, f"6%l+0x{target_rva:x}+{sub}"))

    # Also try: .data section offsets
    for sub in [0, 8, 16, 32, 64, 128]:
        candidate = 0x3200 + sub
        if candidate + 16 <= len(sample):
            offsets_to_try.append((candidate, f".data+{sub}"))

    # Also try: END of .6%l (last 16 non-padding bytes)
    # And the beginning of .6%l
    offsets_to_try.append((0x3800, ".6%l+0"))

    for file_off, label in offsets_to_try:
        result = try_patch(r, sample, rotors, file_off, label)
        log.info(f"Result [{label}]: {result}")
        if "accepted" in result.lower() or "correct" in result.lower():
            log.success(f"SUCCESS! Offset: 0x{file_off:x}")
            break

    r.close()

if __name__ == "__main__":
    main()
