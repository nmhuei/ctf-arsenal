#!/usr/bin/env python3
import ssl
import socket
import subprocess
import os
import sys

DEFAULT_HOST = "impossible-7410a5decef4.chall.nnsc.tf"
DEFAULT_PORT = 1337

def get_proof():
    crate_dir = os.path.join(os.path.dirname(__file__), "..", "challenge", "crypto_impossible")
    res = subprocess.run(
        ["cargo", "run", "--manifest-path", os.path.join(crate_dir, "Cargo.toml"), "--bin", "test_forge"],
        capture_output=True,
        text=True,
        check=True
    )

    proof_str = None
    for line in res.stdout.splitlines():
        if line.startswith("PROOF STRING: "):
            proof_str = line.split("PROOF STRING: ")[1].strip()

    assert proof_str, "Could not obtain forged proof string"
    return proof_str

def solve(host=DEFAULT_HOST, port=DEFAULT_PORT):
    proof_str = get_proof()
    print(f"[+] Forged Proof: {proof_str}")

    print(f"[*] Connecting to TLS {host}:{port}...")
    ctx = ssl.create_default_context()
    s = socket.create_connection((host, port), timeout=15)
    ss = ctx.wrap_socket(s, server_hostname=host)

    banner = ss.recv(1024).decode(errors="replace")
    print(f"[*] Server banner:\n{banner}")

    ss.sendall((proof_str + "\n").encode())
    resp = ss.recv(4096).decode(errors="replace")
    print(f"[+] Server response:\n{resp}")
    ss.close()

    for line in resp.splitlines():
        if "NNS{" in line:
            flag = line[line.index("NNS{"):line.index("}") + 1]
            print(f"[+] Found flag: {flag}")
            flag_file = os.path.join(os.path.dirname(__file__), "..", "flag.txt")
            with open(flag_file, "w") as f:
                f.write(flag + "\n")
            return flag

    return None

if __name__ == "__main__":
    h = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    p = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    solve(h, p)
