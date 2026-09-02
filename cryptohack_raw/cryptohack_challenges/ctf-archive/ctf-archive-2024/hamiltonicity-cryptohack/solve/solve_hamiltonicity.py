#!/usr/bin/env python3
import argparse
import json
import os
import random
import select
import socket
import subprocess
import sys
import time
from hashlib import sha256

P = 0x19dad539e2d348cc3ab07d51f2bb6491d1552aa8cf1db928920fd3d86946aed8805d2e279fa8632dd5fbab8aaf7df1069906b057cc785b7f191ef1b9b5da38cff2e7c64da17bb56a058707d9fd69e546a95e502e556a314c587c7ae36c3d1122e6954f5d81dd9239e02f61b045360187b4caeed271cec1919a0d8a39e855040cf
q = 0xced6a9cf169a4661d583ea8f95db248e8aa9554678edc944907e9ec34a3576c402e9713cfd43196eafdd5c557bef8834c83582be63c2dbf8c8f78dcdaed1c67f973e326d0bddab502c383ecfeb4f2a354af28172ab518a62c3e3d71b61e8891734aa7aec0eec91cf017b0d8229b00c3da65776938e760c8cd06c51cf42a82067
h1 = 250335104192448110684442096964171969189371208477846978499544515755228857598805930673171509152681305793789903169450438090936970626429806187630240086681623358732517929314870247393468568111513100989768455673769015138136779312483203922847547169463972757664497001482465636402329003817055202840451714256443734563502
h2 = 50837518481371967588098771977165879422445597094015682347125264774697010574110399136037637691883034517374621248070926110725252171239208140392324019115211573768989274797050961703999139947885402838647962534519882622024973824201026885393782961783980351898031905383197219266093119145616328556294476943229578292306
comm_params = (P, q, h1, h2)

N = 5
NUM_ROUNDS = 128
# Any directed Hamiltonian cycle is enough for challenge bit 1, because the verifier
# only checks that these committed edges open to 1. It does not compare to the real G.
CYCLE = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]
CYCLE_SET = {(a, b) for a, b in CYCLE}


def pedersen_commit(message: int):
    r = random.randint(0, q)
    return (pow(h1, message, P) * pow(h2, r, P)) % P, r


def hash_committed_graph(G, state: bytes) -> bytes:
    fs_state = sha256(str(comm_params).encode())
    fs_state.update(state)
    first_message = "".join(str(x) for row in G for x in row)
    fs_state.update(first_message.encode())
    return fs_state.digest()


def forge_one_round(fs_state: bytes):
    # Build a matrix that is only guaranteed to open correctly on CYCLE.
    # For challenge=1 the verifier never opens the other 20 entries, and
    # check_graph() only checks dimensions, so A[0][0] can be a cheap nonce.
    A = [[1] * N for _ in range(N)]
    r_by_edge = {}
    for a, b in CYCLE:
        c, r = pedersen_commit(1)
        A[a][b] = c
        r_by_edge[(a, b)] = r

    attempts = 0
    nonce = random.getrandbits(64)
    while True:
        attempts += 1
        A[0][0] = nonce + attempts  # (0,0) is not in CYCLE, so it is never opened.
        new_state = hash_committed_graph(A, fs_state)
        if new_state[-1] & 1:
            rvals = [r_by_edge[(a, b)] for a, b in CYCLE]
            return {"A": A, "z": [CYCLE, rvals]}, new_state, attempts


class LocalTube:
    def __init__(self, argv):
        env = os.environ.copy()
        env.setdefault("FLAG", "crypto{local_test_flag}")
        self.p = subprocess.Popen(
            argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
        )
        self.fd = self.p.stdout.fileno()
        self.buf = b""

    def recv_some(self, timeout=0.2):
        out = b""
        end = time.time() + timeout
        while time.time() < end:
            r, _, _ = select.select([self.fd], [], [], max(0, end - time.time()))
            if not r:
                break
            chunk = os.read(self.fd, 4096)
            if not chunk:
                break
            out += chunk
            if len(chunk) < 4096:
                break
        return out

    def sendline(self, data: bytes):
        self.p.stdin.write(data + b"\n")
        self.p.stdin.flush()

    def close(self):
        try:
            self.p.terminate()
        except Exception:
            pass


class SocketTube:
    def __init__(self, host, port):
        self.s = socket.create_connection((host, port), timeout=10)
        self.s.settimeout(0.2)

    def recv_some(self, timeout=0.2):
        self.s.settimeout(timeout)
        chunks = []
        while True:
            try:
                chunk = self.s.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
                if len(chunk) < 4096:
                    break
            except socket.timeout:
                break
        return b"".join(chunks)

    def sendline(self, data: bytes):
        self.s.sendall(data + b"\n")

    def close(self):
        self.s.close()


def solve(tube):
    fs_state = b""
    banner = tube.recv_some(0.5)
    if banner:
        sys.stdout.buffer.write(banner)
        sys.stdout.buffer.flush()

    total_attempts = 0
    for rnd in range(NUM_ROUNDS):
        payload, fs_state, attempts = forge_one_round(fs_state)
        total_attempts += attempts
        tube.sendline(json.dumps(payload).encode())
        if rnd % 16 == 0:
            print(f"[round {rnd:03d}] ok, attempts={attempts}", file=sys.stderr)

    # Drain output. The service normally closes after printing the flag.
    idle = 0
    while idle < 20:
        chunk = tube.recv_some(0.1)
        if chunk:
            idle = 0
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
            if b"didn't verify" in chunk or b"Traceback" in chunk:
                raise SystemExit("verification failed")
        else:
            idle += 1
            # local process exited
            if hasattr(tube, "p") and tube.p.poll() is not None:
                rest = tube.p.stdout.read() or b""
                if rest:
                    sys.stdout.buffer.write(rest)
                    sys.stdout.buffer.flush()
                break
    print(f"\n[+] total grinding attempts: {total_attempts}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("host", nargs="?", help="remote host, e.g. archive.cryptohack.org")
    ap.add_argument("port", nargs="?", type=int, help="remote port, e.g. 14635")
    ap.add_argument("--local", default=None, help="local chal.py path")
    args = ap.parse_args()

    if args.local:
        tube = LocalTube([sys.executable, "-u", args.local])
    elif args.host and args.port:
        tube = SocketTube(args.host, args.port)
    else:
        ap.error("use --local ./chal.py or provide host port")

    try:
        solve(tube)
    finally:
        tube.close()


if __name__ == "__main__":
    main()
