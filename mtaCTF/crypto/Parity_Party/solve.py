#!/usr/bin/env python3
import sys
import os
import subprocess
import socket
from decimal import Decimal, getcontext
from Crypto.Util.number import long_to_bytes

# Set Decimal precision high enough for 1024-bit binary search
getcontext().prec = 1000

class LocalInterface:
    def __init__(self, cmd):
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

    def readline(self):
        return self.proc.stdout.readline()

    def sendall_lines(self, lines):
        payload = "\n".join(lines) + "\n"
        self.proc.stdin.write(payload)
        self.proc.stdin.flush()

    def close(self):
        self.proc.kill()


class RemoteInterface:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Disable Nagle's algorithm for lowest latency
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.connect((host, port))
        self.reader = self.sock.makefile('r', buffering=1)
        self.writer = self.sock.makefile('w', buffering=1)

    def readline(self):
        return self.reader.readline()

    def sendall_lines(self, lines):
        payload = "\n".join(lines) + "\n"
        self.writer.write(payload)
        self.writer.flush()

    def close(self):
        self.sock.close()


def solve_fast(io):
    # Read parameters
    n_line = io.readline().strip()
    e_line = io.readline().strip()
    c_line = io.readline().strip()

    n = int(n_line.split("=")[1].strip())
    e = int(e_line.split("=")[1].strip())
    c = int(c_line.split("=")[1].strip())

    print(f"[*] N = {n}")
    print(f"[*] e = {e}")
    print(f"[*] c = {c}")

    # OPTIMIZATION: Pipelining / Bulk Sending
    # Since c_k = c * (2^k)^e mod n does not depend on previous oracle replies,
    # we precompute all 1024 ciphertexts and send them in a single batch (1 RTT)!
    print("[*] Precomputing all 1024 ciphertexts...")
    mult = pow(2, e, n)
    ct_list = []
    current_c = c
    for _ in range(1024):
        current_c = (current_c * mult) % n
        ct_list.append(str(current_c))

    print("[*] Sending all 1024 queries at once (pipelining)...")
    io.sendall_lines(ct_list)

    print("[*] Reading all parity responses...")
    parities = []
    for _ in range(1024):
        line = io.readline()
        while "Parity:" not in line:
            line = io.readline()
        parity = int(line.split(":")[-1].strip())
        parities.append(parity)

    # Reconstruct plaintext using binary search
    low = Decimal(0)
    high = Decimal(n)
    for parity in parities:
        mid = (low + high) / 2
        if parity == 1:
            low = mid
        else:
            high = mid

    for cand in [int(high), int(low), int(high) - 1, int(low) + 1]:
        recovered = long_to_bytes(cand)
        if b"{" in recovered and b"}" in recovered:
            print(f"[+] Flag found: {recovered.decode('latin1', errors='ignore')}")
            return recovered

    res = long_to_bytes(int(high))
    print(f"[+] Decrypted: {res}")
    return res


if __name__ == "__main__":
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
        print(f"[*] Connecting to {host}:{port}...")
        io = RemoteInterface(host, port)
    else:
        print("[*] Running locally with chall.py...")
        chall_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chall.py")
        io = LocalInterface([sys.executable, chall_path])

    try:
        solve_fast(io)
    finally:
        io.close()
