#!/usr/bin/env python3
"""
SEKAI CTF 2026 - mikuprotect

Strategy: The rotors (4 DWORDs) are stored somewhere in the binary.
We try multiple candidate offsets where they might be stored,
patch them with the provided rotor values, and submit.
The server checks if the rotors at the expected position(s) match.
"""
from pwn import *
import subprocess
import hashlib
import struct
import time
import sys

HOST = "mikuprotect.chals.sekai.team"
PORT = 1337
context.log_level = 'info'

def solve_pow(challenge):
    result = subprocess.run(challenge, shell=True, capture_output=True, text=True, timeout=120)
    return result.stdout.strip()

def get_challenge():
    r = remote(HOST, PORT)
    r.recvuntil(b'proof of work:\n')
    pow_cmd = r.recvuntil(b'\nsolution: ', drop=True).decode().strip()
    sol = solve_pow(pow_cmd)
    r.sendline(sol.encode())

    r.recvuntil(b'sample_size=')
    sample_size = int(r.recvuntil(b'\n', drop=True).decode())
    r.recvuntil(b'sample_sha256=')
    r.recvuntil(b'\n', drop=True)
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

    # Parse rotors and target
    import re
    text = rest.decode('ascii', errors='replace')
    m = re.search(r"target=b'([^']*)'", text)
    target = m.group(1) if m else ""
    m = re.search(r'rotors? a=0x([0-9a-fA-F]+) b=0x([0-9a-fA-F]+) c=0x([0-9a-fA-F]+) d=0x([0-9a-fA-F]+)', text)
    rotors = [int(m.group(i), 16) for i in range(1, 5)] if m else []

    return r, sample, target, rotors, text

def try_patch_offset(sample, rotors, target_output):
    """Try patching the rotors at various offsets"""
    rotor_bytes = b''
    for r in rotors:
        rotor_bytes += struct.pack('<I', r)

    candidates = []

    # C1: End of .6%l section (last 16 bytes)
    sect_start = 0x3800
    sect_size = 0x266e00
    # Find last non-zero area
    sect = sample[sect_start:sect_start+sect_size]
    for i in range(len(sect)-16, -1, -1):
        if any(b != 0 for b in sect[i:i+16]):
            candidates.append(('6%l_end_minus_' + hex(i), sect_start + i))
            break

    # C2: At specific offsets from .6%l start
    for offset in [0x100, 0x200, 0x300, 0x400, 0x500, 0x1000, 0x2000, 0x4000, 0x8000]:
        candidates.append((f'6%l+0x{offset:x}', sect_start + offset))

    # C3: In .data section
    for offset in [0, 16, 32, 64, 128, 256]:
        candidates.append((f'.data+0x{offset:x}', 0x3200 + offset))

    # C4: End of .text section
    candidates.append(('.text_end-16', 0x400 + 0x2000 - 16))

    # C5: End of binary
    candidates.append(('file_end-16', len(sample) - 16))

    # C6: Beginning of .rdata
    candidates.append(('.rdata+0', 0x2400))
    candidates.append(('.rdata+16', 0x2410))
    candidates.append(('.rdata_end-16', 0x2400 + 0xe00 - 16))

    # C7: Random offsets in .6%l that align with known patterns
    for high_byte in range(256):
        offset = (high_byte << 16) + 0x6000 - 0x3800  # Convert RVA to file offset
        if 0x3800 <= offset <= 0x3800 + 0x266e00 - 16:
            candidates.append((f'RVA 0x{offset-0x3800+0x6000:x}', offset))

    return candidates

def main():
    r, sample, target, rotors, text = get_challenge()
    log.info(f"Target: {repr(target)}")
    log.info(f"Rotors: {[hex(v) for v in rotors]}")

    # Try submitting with original binary first to confirm rejection
    log.info("Submitting ORIGINAL binary...")
    r.send(sample)
    time.sleep(3)
    try:
        resp = r.recv(4096, timeout=10)
        log.info(f"Response: {resp}")
    except:
        pass
    r.close()

if __name__ == "__main__":
    main()
