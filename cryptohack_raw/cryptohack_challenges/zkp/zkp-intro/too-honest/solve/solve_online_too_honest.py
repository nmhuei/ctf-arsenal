#!/usr/bin/env python3
import json
import socket
from Crypto.Util.number import long_to_bytes

HOST = "socket.cryptohack.org"
PORT = 13429

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
        
        # Get challenge data
        init_data = json.loads(f.readline().decode())
        print(f"Init: {init_data}")
        
        # R = 2**(2*128 + 512) = 2**768. Let's send e = 2**1000
        e = 1 << 1000
        resp = send_json(f, {"e": e})
        print(f"Resp: {resp}")
        
        z = resp["z"]
        flag_val = z // e
        r = z % e
        
        print(f"[+] flag_val: {flag_val}")
        print(f"[+] r: {r}")
        print(f"[+] Recovered: {long_to_bytes(flag_val)}")

if __name__ == "__main__":
    main()
