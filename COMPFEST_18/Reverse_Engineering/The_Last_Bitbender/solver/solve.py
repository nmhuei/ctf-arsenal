#!/usr/bin/env python3
import sys
import struct
import socket
import re
from z3 import *

def z3_rol64(x, n):
    return RotateLeft(x, n)

def invert(target_bytes):
    """
    Given 16-byte target output (out1, out2 as two uint64 little-endian),
    uses Z3 to find a 16-byte input (x, y) such that transform(x, y) == target.
    """
    out1_target, out2_target = struct.unpack("<QQ", target_bytes)
    
    s = Solver()
    x = BitVec("x", 64)
    y = BitVec("y", 64)
    
    # Step 1: 64-bit xor
    x1 = x ^ 0xa6f1c0d93b5e2748
    y1 = y
    
    # Step 2: 32-bit mul + rol13 + xor
    x1_low = ZeroExt(32, Extract(31, 0, x1))
    y1_low = ZeroExt(32, Extract(31, 0, y1))
    x2 = x1 + (x1_low * y1_low)
    y2 = z3_rol64(y1, 13)
    x3 = x2 ^ y2
    y3 = y2
    
    # Step 3: 64-bit add + rol29 + imul + add + rol17
    y4 = y3 + x3
    y5 = z3_rol64(y4, 29)
    y6 = y5 * 0xff51afd7ed558ccd
    x4 = x3 + y6
    x5 = z3_rol64(x4, 17)
    
    # Step 4: 32-bit out (xor, add)
    out1 = x5 ^ y6
    out2 = x5 + y6
    
    s.add(out1 == out1_target)
    s.add(out2 == out2_target)
    
    if s.check() == sat:
        m = s.model()
        x_val = m[x].as_long()
        y_val = m[y].as_long()
        return struct.pack("<QQ", x_val, y_val)
    return None

def solve_remote(host, port):
    print(f"[*] Connecting to {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    
    buf = ""
    while True:
        data = s.recv(4096)
        if not data:
            break
        text = data.decode(errors="ignore")
        buf += text
        sys.stdout.write(text)
        sys.stdout.flush()
        
        # Check for hex target pattern (32 hex characters = 16 bytes)
        hex_matches = re.findall(r"([0-9a-fA-F]{32})", text)
        if hex_matches and ("target" in text.lower() or "input" in text.lower() or ":" in text):
            target_hex = hex_matches[-1]
            target_bytes = bytes.fromhex(target_hex)
            print(f"\n[*] Solving target: {target_hex}")
            sol = invert(target_bytes)
            if sol:
                sol_hex = sol.hex()
                print(f"[+] Found solution: {sol_hex}")
                s.sendall(sol_hex.encode() + b"\n")
        
        if "COMPFEST" in buf:
            flag_match = re.search(r"COMPFEST\{[^}]+\}|COMPFEST18\{[^}]+\}", buf)
            if flag_match:
                print(f"\n[🏁] FLAG FOUND: {flag_match.group(0)}")
                break

if __name__ == "__main__":
    if len(sys.argv) == 3:
        solve_remote(sys.argv[1], int(sys.argv[2]))
    else:
        print("Self-test verification:")
        test_target = bytes.fromhex("023a3db6ab0ec7efd2babd484c91f80f")
        sol = invert(test_target)
        print("Self-test solution (hex):", sol.hex())
        print("Usage: python3 solve.py <host> <port>")
