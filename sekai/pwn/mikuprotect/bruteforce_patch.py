#!/usr/bin/env python3
from pwn import *
import subprocess, hashlib, struct, time, sys

HOST = "mikuprotect.chals.sekai.team"
PORT = 1337
context.log_level = 'warn'

def solve_pow(challenge):
    result = subprocess.run(challenge, shell=True, capture_output=True, text=True, timeout=120)
    return result.stdout.strip()

def try_patch(patch_func, label):
    """Patch binary with given function and submit to server"""
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

    import re
    text = rest.decode('ascii', errors='replace')
    m = re.search(r"target=b'([^']*)'", text)
    target = m.group(1) if m else ""
    m = re.search(r'rotors? a=0x([0-9a-fA-F]+) b=0x([0-9a-fA-F]+) c=0x([0-9a-fA-F]+) d=0x([0-9a-fA-F]+)', text)
    rotors = [int(m.group(i), 16) for i in range(1, 5)] if m else []

    patched = patch_func(sample, rotors, target)

    log.info(f"[{label}] Sending {len(patched)} bytes...")
    r.send(patched)

    time.sleep(5)
    try:
        resp = r.recv(4096, timeout=10)
        result = resp.decode('ascii', errors='replace').strip()
        log.info(f"[{label}] Result: {result}")
    except:
        log.info(f"[{label}] No response/timeout")
        result = "timeout"

    r.close()
    return result

def patch_v1_6pctail(data, rotors, target):
    """Patch: write 4 rotors at end of .6%l section padding area"""
    d = bytearray(data)
    rotor_bytes = b''.join(struct.pack('<I', r) for r in rotors)
    # .6%l section ends at 0x3800 + 0x266e00 = 0x2a6600
    # Place rotors at last 16 non-padding bytes
    sect = d[0x3800:0x3800+0x266e00]
    for i in range(len(sect)-16, -1, -1):
        if any(b != 0 for b in sect[i:i+16]):
            # The rotors go at offset i
            log.info(f"v1: Patching at .6%l+0x{i:x}")
            for j, r in enumerate(rotors):
                struct.pack_into('<I', d, 0x3800 + i + j*4, r)
            break
    return bytes(d)

def patch_v2_datasect(data, rotors, target):
    """Patch: write 4 rotors at beginning of .data section"""
    d = bytearray(data)
    for j, r in enumerate(rotors):
        struct.pack_into('<I', d, 0x3200 + 16 + j*4, r)  # Right after the header
    return bytes(d)

def patch_v3_enctail(data, rotors, target):
    """Patch: XOR target with rotors, place at end of .6%l"""
    d = bytearray(data)
    target_b = target.encode() if isinstance(target, str) else target
    rotor_bytes = b''.join(struct.pack('<I', r) for r in rotors)

    encoded = bytearray(len(target_b))
    for i in range(len(target_b)):
        encoded[i] = target_b[i] ^ rotor_bytes[i % 16]

    # Place at .6%l+0x266df0 (just before zero padding)
    patch_off = 0x3800 + 0x266df0
    for i, b in enumerate(encoded):
        d[patch_off + i] = b
    return bytes(d)

def patch_v4_str_replace(data, rotors, target):
    """Find place where original string might be and replace with target"""
    # Quick try: just append to end of file
    d = bytearray(data)
    rotor_bytes = b''.join(struct.pack('<I', r) for r in rotors)
    target_b = target.encode() if isinstance(target, str) else target
    encoded = bytearray(len(target_b))
    for i in range(len(target_b)):
        encoded[i] = target_b[i] ^ rotor_bytes[i % 16]
    d.extend(encoded)
    return bytes(d)

def patch_v5_plaintext(data, rotors, target):
    """Write plain target string at a known offset in .data"""
    d = bytearray(data)
    target_b = target.encode() if isinstance(target, str) else target
    # Write to .data at offset 0x80
    for i, b in enumerate(target_b):
        if 0x3280 + i < len(d):
            d[0x3280 + i] = b
    return bytes(d)

def patch_v6_rotors_at_rdata(data, rotors, target):
    """Write rotors at the license string location"""
    d = bytearray(data)
    # "your vmprotect license is banned" is at file offset 0x26b4
    for j, r in enumerate(rotors):
        struct.pack_into('<I', d, 0x26b4 + j*4, r)
    return bytes(d)

# Try different strategies
strategies = [
    patch_v1_6pctail,
    patch_v2_datasect,
    # patch_v3_enctail,
    # patch_v4_str_replace,
    # patch_v5_plaintext,
    # patch_v6_rotors_at_rdata,
]

for i, strategy in enumerate(strategies):
    result = try_patch(strategy, f"v{i+1}")
    print(f"Strategy v{i+1}: {result}")
