#!/usr/bin/env python3
import socket
import time

def recv_until(s: socket.socket, target: bytes) -> bytes:
    buf = b""
    while target not in buf:
        chunk = s.recv(4096)
        if not chunk:
            break
        buf += chunk
    return buf

def solve_speed_challenge(s: socket.socket) -> str:
    recv_until(s, b"> ")
    s.sendall(b"5\n")
    data = recv_until(s, b"Your Classification Bits: ").decode()
    # Find Challenge Words: ...
    for line in data.splitlines():
        if "Challenge Words:" in line:
            words = line.split("Challenge Words:")[1].strip().split()
            bits = "".join("1" if "b" in w else "0" for w in words)
            s.sendall(f"{bits}\n".encode())
            break
    res = recv_until(s, b"---------------------------------------------------").decode()
    return res

def solve_encrypted_flag(s: socket.socket) -> str:
    recv_until(s, b"> ")
    s.sendall(b"2\n")
    data = recv_until(s, b"---------------------------------------------------").decode()
    flag_line = ""
    lines = data.splitlines()
    for i, line in enumerate(lines):
        if "Encrypted Flag Words" in line and i + 1 < len(lines):
            flag_line = lines[i + 1].strip()
            break
    words = [w.strip() for w in flag_line.split(",") if w.strip()]
    bits = "".join("1" if "b" in w else "0" for w in words)
    flag_bytes = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
    return flag_bytes.decode("utf-8", errors="ignore")

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 13374

    print("[*] Testing Method 1 (Speed Challenge)...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", port))
    out = solve_speed_challenge(s)
    print("Output:\n", out)
    s.close()

    print("[*] Testing Method 2 (Decrypting Flag Words)...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", port))
    flag = solve_encrypted_flag(s)
    print("Decrypted Flag:", flag)
    s.close()
