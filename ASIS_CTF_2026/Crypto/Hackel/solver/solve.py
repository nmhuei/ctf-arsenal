#!/usr/bin/env python3
# Solution for: Hackel (Crypto)
import argparse
import os
import socket
import subprocess
import sys
import threading
import time

DEFAULT_HOST = '65.109.208.91'
DEFAULT_PORT = 3771

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

def run_solver(host: str, port: int) -> str | None:
    print(f"[*] Connecting to {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10.0)
    s.connect((host, port))

    out = solve_speed_challenge(s)
    flag = None
    for line in out.splitlines():
        if "[+] FLAG:" in line:
            flag = line.split("[+] FLAG:")[1].strip()
            print(f"[+] Found flag via speed test: {flag}")

    if not flag:
        print("[-] Speed challenge did not return flag, trying encrypted flag words...")
        flag = solve_encrypted_flag(s)
        print(f"[+] Decrypted flag: {flag}")

    s.close()
    return flag

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--remote', metavar='HOST:PORT', help='Connect to remote/local service')
    parser.add_argument('--local', action='store_true', help='Run against ephemeral local server')
    return parser.parse_args()

def main():
    args = parse_args()
    if args.local or (not args.remote and not os.environ.get("USE_REMOTE")):
        # By default when invoked without arguments or with --local, verify locally
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        chall_py = os.path.join(base_dir, "challenge", "Hackel", "hackel.py")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.join(base_dir, "challenge", "Hackel") + ":" + os.path.join(base_dir, "script")

        # Find free port
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            free_port = probe.getsockname()[1]

        proc = subprocess.Popen(
            [sys.executable, chall_py, "--host", "127.0.0.1", "--port", str(free_port)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(0.3)
        try:
            flag = run_solver("127.0.0.1", free_port)
        finally:
            proc.terminate()
            proc.wait()
    else:
        remote_target = args.remote or f"{DEFAULT_HOST}:{DEFAULT_PORT}"
        host, port = remote_target.rsplit(":", 1)
        flag = run_solver(host, int(port))

    if flag and "dummy" not in flag:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        flag_path = os.path.join(base_dir, "flag.txt")
        with open(flag_path, "w") as f:
            f.write(flag + "\n")
        print(f"[+] Flag saved to {flag_path}")

if __name__ == '__main__':
    main()
