#!/usr/bin/env python3
import json
import socket
import random

HOST = "socket.cryptohack.org"
PORT = 13427

p = 0x1ed344181da88cae8dc37a08feae447ba3da7f788d271953299e5f093df7aaca987c9f653ed7e43bad576cc5d22290f61f32680736be4144642f8bea6f5bf55ef
q = 0xf69a20c0ed4465746e1bd047f57223dd1ed3fbc46938ca994cf2f849efbd5654c3e4fb29f6bf21dd6abb662e911487b0f9934039b5f20a23217c5f537adfaaf7
g = 2

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
        
        # Get first challenge and e, y
        init_data = json.loads(f.readline().decode())
        print(f"Init: {init_data}")
        
        e = init_data["e"]
        y = init_data["y"]
        
        # Choose random z in range(q)
        z = random.randint(1, q - 1)
        
        # Compute a = g^z * (y^e)^-1 mod p
        inv_ye = pow(pow(y, e, p), -1, p)
        a = (pow(g, z, p) * inv_ye) % p
        
        # Send a, z
        resp = send_json(f, {"a": a, "z": z})
        print(f"Resp: {resp}")

if __name__ == "__main__":
    main()
