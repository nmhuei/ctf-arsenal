#!/usr/bin/env python3
import json
import socket
import random

HOST = "socket.cryptohack.org"
PORT = 13425

p = 0x1ed344181da88cae8dc37a08feae447ba3da7f788d271953299e5f093df7aaca987c9f653ed7e43bad576cc5d22290f61f32680736be4144642f8bea6f5bf55ef
q = 0xf69a20c0ed4465746e1bd047f57223dd1ed3fbc46938ca994cf2f849efbd5654c3e4fb29f6bf21dd6abb662e911487b0f9934039b5f20a23217c5f537adfaaf7
g = 2
w = 0x5a0f15a6a725003c3f65238d5f8ae4641f6bf07ebf349705b7f1feda2c2b051475e33f6747f4c8dc13cd63b9dd9f0d0dd87e27307ef262ba68d21a238be00e83

def recv_until_json_or_banner(f):
    line = f.readline()
    if not line:
        raise EOFError("server closed connection")
    return line.decode(errors="replace").strip()

def send_json(f, obj):
    f.write((json.dumps(obj) + "\n").encode())
    f.flush()
    line = recv_until_json_or_banner(f)
    try:
        return json.loads(line)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Expected JSON, got: {line!r}") from e

def main():
    with socket.create_connection((HOST, PORT), timeout=10) as sock:
        f = sock.makefile("rwb", buffering=0)
        
        # Read banner
        banner = f.readline().decode()
        print(f"Banner: {banner.strip()}")
        
        # 1. Choose random r
        r = random.randint(1, q - 1)
        a = pow(g, r, p)
        
        # 2. Send a
        resp1 = send_json(f, {"a": a})
        print(f"Resp1: {resp1}")
        
        e = resp1["e"]
        
        # 3. Calculate z = (r + e * w) % q
        z = (r + e * w) % q
        
        # 4. Send z
        resp2 = send_json(f, {"z": z})
        print(f"Resp2: {resp2}")

if __name__ == "__main__":
    main()
