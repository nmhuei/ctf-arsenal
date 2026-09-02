#!/usr/bin/env python3
import os
import secrets
import socketserver
import sys
import threading

import numpy as np

HOST = "0.0.0.0"
PORT = 9999
N = 50
Q = 10007
MAX_SAMPLES = 320
SECRET_BOUND = 3
NOISE_VALUES = (-1, 0, 1)

BANNER = b"""Lattice in the Machine\nquantum-safe AI communication console\ncommands: params | sample | encrypt | quit\n> """

_rng = np.random.default_rng()
_secret = _rng.integers(-SECRET_BOUND, SECRET_BOUND + 1, size=N, dtype=np.int64)
_lock = threading.Lock()
_sample_count = 0


def centered(x):
    x = int(x) % Q
    if x > Q // 2:
        x -= Q
    return x


def encode_flag(flag):
    bits = []
    for byte in flag.encode():
        for i in range(8):
            bits.append((byte >> i) & 1)
    return bits


def sample_pair():
    a = _rng.integers(0, Q, size=N, dtype=np.int64)
    e = int(_rng.choice(NOISE_VALUES))
    b = int((int(np.dot(a, _secret)) + e) % Q)
    return a, b


def encrypt_bit(bit):
    a, b = sample_pair()
    if bit:
        b = (b + Q // 2) % Q
    return a, b


def line_for_pair(a, b):
    return "A=" + ",".join(str(int(x)) for x in a) + f"; b={int(b)}\n"


class Handler(socketserver.BaseRequestHandler):
    def send(self, data):
        if isinstance(data, str):
            data = data.encode()
        self.request.sendall(data)

    def recvline(self):
        data = bytearray()
        while len(data) < 4096:
            chunk = self.request.recv(1)
            if not chunk:
                return None
            if chunk == b"\n":
                break
            if chunk != b"\r":
                data.extend(chunk)
        return bytes(data).decode(errors="ignore").strip()

    def handle(self):
        global _sample_count
        self.send(BANNER)
        while True:
            cmd = self.recvline()
            if cmd is None:
                return
            cmd = cmd.lower()
            if cmd == "params":
                self.send(f"n={N}\nq={Q}\nsamples_left={max(0, MAX_SAMPLES - _sample_count)}\n> ")
            elif cmd == "sample":
                with _lock:
                    if _sample_count >= MAX_SAMPLES:
                        self.send("error: sample budget exhausted\n> ")
                        continue
                    _sample_count += 1
                a, b = sample_pair()
                self.send(line_for_pair(a, b))
                self.send("> ")
            elif cmd == "encrypt":
                flag = os.environ.get("FLAG", "flag{local_dev_dynamic_flag_placeholder}")
                bits = encode_flag(flag)
                self.send(f"count={len(bits)}\n")
                for bit in bits:
                    a, b = encrypt_bit(bit)
                    self.send(line_for_pair(a, b))
                self.send("> ")
            elif cmd in ("quit", "exit"):
                self.send("bye\n")
                return
            else:
                self.send("error: unknown command\n> ")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    with Server((HOST, PORT), Handler) as srv:
        srv.serve_forever()
