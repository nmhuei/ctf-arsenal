#!/usr/bin/env python3
import socket
import struct
import hashlib
import json
import ctypes
import os
import io
import zipfile

HOST = "34.2.147.230"
PORT = 7010

TOKEN = "BGLPROOF{orion-lab__cap-A812__loader-4787__implant-BG-94C2A04EC6__build-542715c2e46252e4d790__config-360251a5def08d12cb71e72d5a1609b0d34c9dfc9520197ad8b0cc2cd7cfb76b__archive-4bd20e26a2e63e75af61b07af3cf5dc219ca11a018588a3ce0ee4564338cf64a__digest-836d4fce93ec7b3077ab7c97820d29515ea5609cf346e40b76973ca37e2418ed}"

def solve():
    print(f"[*] Connecting to {HOST}:{PORT}...")
    s = socket.socket()
    s.settimeout(5)
    s.connect((HOST, PORT))

    buf = ""
    while True:
        try:
            chunk = s.recv(1024).decode(errors="ignore")
            if not chunk: break
            buf += chunk
            if "Answer:" in buf or ">" in buf:
                break
        except:
            break

    print(f"[*] Submitting token:\n{TOKEN}")
    s.sendall(TOKEN.encode() + b"\n")

    res = ""
    while True:
        try:
            chunk = s.recv(1024).decode(errors="ignore")
            if not chunk: break
            res += chunk
        except:
            break
    s.close()

    print("\n" + "="*70)
    print(res)
    print("="*70)

    import re
    flag_match = re.search(r"COMPFEST18\{[^}]+\}", res)
    if flag_match:
        print(f"\n[🏁] FLAG: {flag_match.group(0)}")
        return flag_match.group(0)

if __name__ == "__main__":
    solve()
