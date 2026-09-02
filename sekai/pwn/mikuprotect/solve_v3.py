#!/usr/bin/env python3
"""
SEKAI CTF 2026 - mikuprotect solver
Protocol: One connection with 10 rounds.
Round 1: sample + target + rotors → submit patched → round 2 → ... → flag
"""
from pwn import *
import subprocess, hashlib, struct, time, re, sys

HOST = "mikuprotect.chals.sekai.team"
PORT = 1337
context.log_level = 'info'

def solve_pow(challenge):
    result = subprocess.run(challenge, shell=True, capture_output=True, text=True, timeout=120)
    return result.stdout.strip()

def find_rotors(payload):
    """Find rotor values in a sample by checking all 16-byte aligned groups"""
    # Try looking for the known rotor pattern signature
    # Rotors should be 4 consecutive DWORDs in .6%l section (file offset 0x3800)
    sect = payload[0x3800:]
    results = []
    for i in range(0, len(sect) - 16, 4):  # DWORD-aligned
        dw = list(struct.unpack('<IIII', sect[i:i+16]))
        # Rotors tend to be "random-looking" 32-bit values
        # with all 4 DWORDs being non-zero and not looking like code
        if all(d != 0 for d in dw):
            # Check if they look like VM pcode (small values, patterns)
            is_code = any(d < 0x100 and d != 0 for d in dw)  # small constants look like VM opcodes
            if not is_code:
                results.append((i, dw))
    return results[:5]  # Return top 5 candidates

def has_embedded_target(binary, target_str):
    """Check if the target string is embedded anywhere in the binary"""
    return target_str.encode() in binary

def main():
    r = remote(HOST, PORT)

    # PoW
    r.recvuntil(b'proof of work:\n')
    pow_cmd = r.recvuntil(b'\nsolution: ', drop=True).decode().strip()
    log.info(f"PoW: {pow_cmd[:50]}...")
    sol = solve_pow(pow_cmd)
    r.sendline(sol.encode())

    round_num = 1
    while round_num <= 10:
        log.info(f"\n{'='*60}")
        log.info(f"Round {round_num}/10")
        log.info(f"{'='*60}")

        # Read round metadata
        try:
            r.recvuntil(b'sample_size=', timeout=30)
        except:
            log.info("No more rounds, reading final response...")
            time.sleep(2)
            try:
                resp = r.recv(65536, timeout=10)
                log.info(f"Final: {resp}")
            except:
                pass
            break

        sample_size_str = r.recvuntil(b'\n', drop=True).decode()
        sample_size = int(sample_size_str)

        r.recvuntil(b'sample_sha256=')
        expected_sha = r.recvuntil(b'\n', drop=True).decode()

        r.recvuntil(b'sample_raw:\n')

        # Read binary
        sample = b""
        while len(sample) < sample_size:
            chunk = r.recv(min(65536, sample_size - len(sample)), timeout=30)
            if not chunk: break
            sample += chunk

        actual_sha = hashlib.sha256(sample).hexdigest()
        if actual_sha != expected_sha:
            log.warning(f"SHA256 mismatch! Expected {expected_sha}, got {actual_sha}")

        # Read post-binary data (target + rotors)
        time.sleep(0.5)
        post = b""
        while True:
            try:
                c = r.recv(4096, timeout=5)
                if not c: break
                post += c
            except: break

        text = post.decode('ascii', errors='replace')
        log.info(f"Post data: {text[:300]}")

        # Parse target
        m = re.search(r"target=b'([^']*)'", text)
        target = m.group(1) if m else ""

        # Parse rotors
        m = re.search(r'rotors? a=0x([0-9a-fA-F]+) b=0x([0-9a-fA-F]+) c=0x([0-9a-fA-F]+) d=0x([0-9a-fA-F]+)', text)
        rotors = [int(m.group(i), 16) for i in range(1, 5)] if m else []

        log.info(f"Target: {repr(target)}")
        log.info(f"Rotors: {[hex(v) for v in rotors]}")
        log.info(f"Sample: {len(sample)} bytes")

        # Check if target string is embedded in sample
        target_bytes = target.encode()
        if target_bytes in sample:
            idx = sample.index(target_bytes)
            log.info(f"Target already embedded at file offset 0x{idx:x}")
        else:
            log.info("Target NOT found in sample - needs rotor patching")

        # Find rotors in the sample
        rotor_offset = None
        rotor_dwords = struct.pack('<IIII', *rotors)
        sect_start = 0x3800
        sect = sample[sect_start:]

        for i in range(0, len(sect) - 16, 1):
            if sect[i:i+16] == rotor_dwords:
                rotor_offset = sect_start + i
                log.success(f"Rotors found at file offset 0x{rotor_offset:x}")
                break

        if rotor_offset is None:
            log.info("Rotors not found as plain DWORDs. Trying alternative search...")
            # Maybe the rotors are in the binary but with a different layout?
            # Or maybe the challenge works differently - let's try sending the binary as-is
            log.info("Sending original binary (no patch)...")
            r.send(sample)
        else:
            # Rotors already match! Binary doesn't need patching?
            # But the challenge says we must patch...
            # Maybe I should XOR the target and write it somewhere?
            log.info(f"Rotors at offset 0x{rotor_offset:x} already match server values")
            log.info("Sending patched binary (with same rotors)...")
            r.send(sample)

        # Wait for response
        time.sleep(5)
        try:
            resp = r.recv(65536, timeout=15)
            resp_text = resp.decode('ascii', errors='replace')
            log.info(f"Response: {resp_text[:500]}")

            if "sekai" in resp_text.lower():
                log.success(f"FLAG: {resp_text}")
            elif "incorrect" in resp_text.lower() or "wrong" in resp_text.lower():
                log.warning("Rejected")
                break
            elif "correct" in resp_text.lower() or "next" in resp_text.lower():
                round_num += 1
            elif "round" in resp_text:
                # Try to parse next round from response
                log.info("Next round data in response")
                # The response might already contain the next round's data
                # Push it back to parse
                break
            else:
                log.info("Unknown response, trying to continue...")
                round_num += 1
        except Exception as e:
            log.warning(f"No response: {e}")
            break

    # Read any remaining data
    time.sleep(2)
    try:
        final = r.recv(65536, timeout=10)
        log.info(f"Final data: {final.decode('ascii', errors='replace')}")
    except:
        pass

    r.close()

if __name__ == "__main__":
    main()
