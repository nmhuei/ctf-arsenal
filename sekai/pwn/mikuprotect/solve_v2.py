#!/usr/bin/env python3
"""
SEKAI CTF 2026 - mikuprotect solver
Strategy: Find rotor offset by comparing samples, then patch & submit.
"""
from pwn import *
import subprocess, hashlib, struct, time, re

HOST = "mikuprotect.chals.sekai.team"
PORT = 1337
context.log_level = 'info'

ROTOR_OFFSET = None  # Will be determined

def solve_pow(challenge):
    result = subprocess.run(challenge, shell=True, capture_output=True, text=True, timeout=120)
    return result.stdout.strip()

def download_one():
    """Connect, solve PoW, download sample, get target+rotors"""
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
    post = b""
    while True:
        try:
            c = r.recv(4096, timeout=5)
            if not c: break
            post += c
        except: break

    text = post.decode('ascii', errors='replace')

    m = re.search(r"target=b'([^']*)'", text)
    target = m.group(1) if m else ""
    m = re.search(r'rotors? a=0x([0-9a-fA-F]+) b=0x([0-9a-fA-F]+) c=0x([0-9a-fA-F]+) d=0x([0-9a-fA-F]+)', text)
    rotors = [int(m.group(i), 16) for i in range(1,5)] if m else []

    return r, sample, target, rotors, text

def find_rotor_offset(sample1, rotors1, sample2, rotors2):
    """Compare two samples to find the 16-byte rotor storage location"""
    # The rotors are stored as 4 consecutive LE DWORDs
    rotor_bytes = b''.join(struct.pack('<I', r) for r in rotors)

    # Search in .6%l section (file offset 0x3800, size up to sample size)
    sect_start = 0x3800
    sect = sample1[sect_start:]

    # Search for the 16-byte pattern that MATCHES one of our rotor sets
    # (since we're looking for the location, not the values)
    # Strategy: find 16-byte blocks where sample2 has rotor2 values
    expected_new = b''.join(struct.pack('<I', r) for r in rotors2)

    for i in range(0, len(sect) - 16, 1):
        block = sect[i:i+16]
        # Check if sample2 at this offset matches rotors2
        if sample2[sect_start + i:sect_start + i + 16] == expected_new:
            log.success(f"Found rotor offset: .6%l+0x{i:x} (file 0x{sect_start+i:x})")
            log.info(f"  Sample1 at offset: {[hex(struct.unpack('<I', sect[i+j*4:i+j*4+4])[0]) for j in range(4)]}")
            return sect_start + i

    log.error("Rotor offset not found!")
    return None

def patch_rotors(sample, rotors, offset):
    """Patch 4 rotor DWORDs at given offset"""
    d = bytearray(sample)
    for j, r in enumerate(rotors):
        struct.pack_into('<I', d, offset + j*4, r)
    return bytes(d)

def main():
    global ROTOR_OFFSET

    log.info("Step 1: Calibrating - finding rotor offset")

    # Download 2 samples with different targets
    log.info("Downloading sample A...")
    r1, s1, t1, rots1, _ = download_one()
    r1.close()
    log.info(f"  Target: {repr(t1)}")
    log.info(f"  Rotors: {[hex(v) for v in rots1]}")
    log.info(f"  Size: {len(s1)} bytes")

    log.info("Downloading sample B...")
    r2, s2, t2, rots2, _ = download_one()
    r2.close()
    log.info(f"  Target: {repr(t2)}")
    log.info(f"  Rotors: {[hex(v) for v in rots2]}")
    log.info(f"  Size: {len(s2)} bytes")

    offset = find_rotor_offset(s1, rots1, s2, rots2)
    if offset is None:
        log.error("Could not determine rotor offset!")
        return

    ROTOR_OFFSET = offset

    # Verify: check if the OLD rotors match the first sample's reported rotors
    old_rotors = struct.unpack('<IIII', s1[offset:offset+16])
    new_rotors = struct.unpack('<IIII', s2[offset:offset+16])
    log.info(f"  Sample A binary rotors: {[hex(v) for v in old_rotors]}")
    log.info(f"  Sample A server rotors: {[hex(v) for v in rots1]}")
    log.info(f"  Sample B binary rotors: {[hex(v) for v in new_rotors]}")
    log.info(f"  Sample B server rotors: {[hex(v) for v in rots2]}")

    # Now do all 10 rounds
    log.info("\nStep 2: Solving rounds 1-10")

    for round_idx in range(1, 11):
        log.info(f"\n{'='*60}")
        log.info(f"Round {round_idx}/10")
        log.info(f"{'='*60}")

        r, sample, target, rotors, prompt = download_one()
        log.info(f"  Target: {repr(target)}")
        log.info(f"  Rotors: {[hex(v) for v in rotors]}")

        # Check what's currently at the rotor offset
        current = struct.unpack('<IIII', sample[offset:offset+16])
        log.info(f"  Current binary rotors: {[hex(v) for v in current]}")
        log.info(f"  New rotors to patch:   {[hex(v) for v in rotors]}")

        # Patch
        patched = patch_rotors(sample, rotors, offset)
        new_current = struct.unpack('<IIII', patched[offset:offset+16])
        log.info(f"  After patch:            {[hex(v) for v in new_current]}")

        # Send
        log.info("  Sending patched binary...")
        r.send(patched)

        time.sleep(5)
        try:
            resp = r.recv(65536, timeout=15)
            resp_text = resp.decode('ascii', errors='replace')
            log.info(f"  Response: {resp_text.strip()}")

            if "correct" in resp_text.lower() or "accept" in resp_text.lower() or "sekai" in resp_text.lower():
                log.success(f"Round {round_idx} passed!")
            elif "wrong" in resp_text.lower() or "reject" in resp_text.lower() or "error" in resp_text.lower():
                log.warning(f"Round {round_idx} rejected")
        except Exception as e:
            log.warning(f"  No response: {e}")

        r.close()

if __name__ == "__main__":
    main()
