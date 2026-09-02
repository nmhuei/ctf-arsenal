#!/usr/bin/env python3
"""
SEKAICTF 2026 - mikuprotect

Challenge: Server sends a VMProtect-protected Windows PE (x86-64) and
a target output string. We must patch the VM pcode so the binary prints
the requested string. The "rotors" hint provides 4 DWORD parameters.

Strategy: The 4 rotor DWORDs are stored at a FIXED offset within the
binary. We find them by looking for 4 consecutive DWORDs that change
when the target string changes (by comparing samples from different rounds).
Then we patch those 4 DWORDs with the provided rotor values.

NOTE: This is an initial attempt - the actual patching strategy depends
on the challenge design.
"""

from pwn import *
import subprocess
import hashlib
import struct
import sys
import os
import tempfile

HOST = "mikuprotect.chals.sekai.team"
PORT = 1337
context.log_level = 'info'

def solve_pow(challenge):
    """Solve proof-of-work"""
    result = subprocess.run(challenge, shell=True, capture_output=True, text=True, timeout=120)
    return result.stdout.strip()

def connect_and_download():
    """Connect to server, solve PoW, download binary and get target"""
    r = remote(HOST, PORT)

    # PoW
    r.recvuntil(b'proof of work:\n')
    pow_cmd = r.recvuntil(b'\nsolution: ', drop=True).decode().strip()
    log.info(f"PoW: {pow_cmd[:60]}...")

    sol = solve_pow(pow_cmd)
    log.info(f"Solved PoW ({len(sol)} chars)")
    r.sendline(sol.encode())

    # Read sample metadata
    r.recvuntil(b'sample_size=')
    sample_size = int(r.recvuntil(b'\n', drop=True).decode())

    r.recvuntil(b'sample_sha256=')
    expected_sha = r.recvuntil(b'\n', drop=True).decode()

    r.recvuntil(b'sample_raw:\n')

    # Read binary
    sample = b""
    while len(sample) < sample_size:
        chunk = r.recv(min(65536, sample_size - len(sample)), timeout=30)
        if not chunk:
            break
        sample += chunk

    actual_sha = hashlib.sha256(sample).hexdigest()
    assert actual_sha == expected_sha, "SHA256 mismatch!"
    log.info(f"Downloaded {len(sample)} bytes")

    # Read target info
    time.sleep(0.5)
    post = b""
    while True:
        try:
            chunk = r.recv(4096, timeout=5)
            if not chunk:
                break
            post += chunk
        except:
            break

    # Parse target from post data
    post_str = post.decode('ascii', errors='replace')

    # Extract round number, target, rotors
    round_num = 1
    target_str = ""
    rotor_values = [0, 0, 0, 0]

    for line in post_str.split('\n'):
        if 'round' in line:
            parts = line.split()
            for p in parts:
                if p.startswith('round'):
                    try:
                        round_num = int(p.split('/')[0].replace('round', ''))
                    except:
                        pass
        if 'target=' in line:
            import re
            m = re.search(r"target=b'([^']*)'", line)
            if m:
                target_str = m.group(1)
        if 'rotors' in line or 'rotor' in line:
            m = re.search(r'rotors? a=0x([0-9a-fA-F]+) b=0x([0-9a-fA-F]+) c=0x([0-9a-fA-F]+) d=0x([0-9a-fA-F]+)', line)
            if m:
                rotor_values = [int(m.group(1), 16), int(m.group(2), 16),
                                int(m.group(3), 16), int(m.group(4), 16)]

    return r, sample, round_num, target_str, rotor_values, post

def patch_binary(binary, rotors):
    """
    Patch the binary with new rotor values.
    We'll try finding the rotor storage location by looking for patterns.
    """
    data = bytearray(binary)

    # The rotor values are 4 DWORDs (16 bytes total) stored somewhere in the binary.
    # Since this is VMProtect, they should be in the .6%l section.
    # Let's try the approach: search for the 4 DWORDs at the end of the .6%l section,
    # or in the .data section, or at other predictable locations.

    # .6%l section: file offset 0x3800, size 0x266e00
    # .data section: file offset 0x3200, size 0x200

    # Strategy 1: The rotors might be 4 consecutive DWORDs in the .data section
    # Try patching at various offsets

    # Let's patch the rotors as 4 consecutive LE DWORDs at each candidate offset
    # and try to deduce which is correct

    rotor_bytes = b''
    for r in rotors:
        rotor_bytes += struct.pack('<I', r)

    return data

def try_submit(r, patched_binary, post_prefix):
    """Send patched binary back to server"""
    # Send the patched binary
    import hashlib
    sha = hashlib.sha256(patched_binary).hexdigest()
    log.info(f"Sending patched binary (SHA256: {sha}, size: {len(patched_binary)})")

    # The server might expect the binary in raw format
    r.send(patched_binary + b'\n')

    # Read response
    time.sleep(2)
    response = b""
    while True:
        try:
            chunk = r.recv(4096, timeout=5)
            if not chunk:
                break
            response += chunk
        except:
            break

    return response.decode('ascii', errors='replace')

def main():
    """Main solve loop - 10 rounds"""
    all_samples = []

    for round_idx in range(10):
        log.info(f"\n{'='*60}")
        log.info(f"Round {round_idx + 1}/10")
        log.info(f"{'='*60}")

        r, sample, round_num, target_str, rotor_values, post = connect_and_download()

        log.info(f"Target: {repr(target_str)}")
        log.info(f"Rotors: {[hex(v) for v in rotor_values]}")

        all_samples.append((round_num, sample, target_str, rotor_values))

        # For now, just save the binary to analyze
        with open(f'/tmp/round{round_num}_sample.exe', 'wb') as f:
            f.write(sample)

        # Try to patch and submit
        # For first attempt, just pass through and see what server expects
        patched = patch_binary(sample, rotor_values)

        # Send back patched binary
        # Server waits for the patched binary
        log.info("Sending patched binary...")

        # Send raw binary bytes
        r.send(sample)

        # Read response
        import time
        time.sleep(5)
        try:
            resp = r.recv(65536, timeout=10)
            log.info(f"Response: {resp}")
        except:
            log.warning("No response, might be waiting...")
            try:
                resp = r.recv(4096, timeout=30)
                log.info(f"Response (after wait): {resp}")
            except:
                log.error("Still no response")

        r.close()

if __name__ == "__main__":
    main()
