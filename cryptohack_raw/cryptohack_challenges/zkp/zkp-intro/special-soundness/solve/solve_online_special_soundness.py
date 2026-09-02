#!/usr/bin/env python3
import json
import socket
from Crypto.Util.number import long_to_bytes

HOST = "socket.cryptohack.org"
PORT = 13426

q = 0xf69a20c0ed4465746e1bd047f57223dd1ed3fbc46938ca994cf2f849efbd5654c3e4fb29f6bf21dd6abb662e911487b0f9934039b5f20a23217c5f537adfaaf7

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
        
        # Get first challenge A1
        # Wait, the server immediately sends a dictionary
        init_data = json.loads(f.readline().decode())
        print(f"Init: {init_data}")
        
        # Send e1
        e1 = 12345
        resp1 = send_json(f, {"e": e1})
        print(f"Resp1: {resp1}")
        
        z1 = resp1["z"]
        
        # Prover immediately sends the second challenge (no input required from us for CHALLENGE2)
        challenge2 = json.loads(f.readline().decode())
        print(f"Challenge2: {challenge2}")
        
        # Send e2
        e2 = 54321
        resp2 = send_json(f, {"e": e2})
        print(f"Resp2: {resp2}")
        
        z2 = resp2["z2"]
        
        # Extract flag: flag = (z2 - z1) * (e2 - e1)^-1 mod q
        inv_de = pow(e2 - e1, -1, q)
        flag_val = ((z2 - z1) * inv_de) % q
        
        flag_bytes = long_to_bytes(flag_val)
        print(f"[+] Recovered: {flag_bytes}")

if __name__ == "__main__":
    main()
