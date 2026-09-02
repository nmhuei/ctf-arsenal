#!/usr/bin/env python3
import argparse
import socket
import subprocess
import sys
from typing import Iterable

PBOXES = [
    [4, 0, 3, 2, 6, 8, 1, 13, 16, 7, 15, 12, 11, 9, 14, 10, 17, 5],
    [6, 13, 17, 8, 7, 11, 15, 5, 0, 10, 4, 16, 1, 3, 14, 12, 9, 2],
    [9, 17, 13, 11, 4, 10, 16, 8, 14, 7, 15, 1, 6, 5, 12, 3, 0, 2],
    [3, 14, 17, 5, 11, 2, 10, 12, 1, 16, 6, 9, 0, 4, 8, 15, 13, 7],
    [6, 9, 11, 16, 8, 10, 7, 14, 15, 12, 5, 1, 4, 0, 3, 17, 13, 2],
    [0, 13, 9, 6, 2, 15, 5, 11, 17, 14, 12, 16, 7, 3, 10, 4, 1, 8],
    [7, 0, 8, 13, 16, 1, 15, 17, 5, 14, 10, 3, 2, 12, 9, 4, 6, 11],
    [10, 4, 17, 7, 2, 1, 11, 13, 5, 6, 16, 8, 9, 0, 12, 3, 15, 14],
]

SBOX = [
    74, 3, 10, 192, 95, 220, 206, 247, 200, 66, 139, 64, 39, 5, 62, 207,
    63, 81, 120, 30, 55, 121, 219, 107, 45, 156, 237, 211, 190, 125, 35,
    162, 248, 216, 20, 26, 166, 80, 122, 37, 254, 177, 225, 14, 33, 76,
    181, 227, 168, 51, 161, 218, 41, 18, 209, 71, 236, 25, 150, 241, 228,
    119, 97, 85, 129, 194, 130, 195, 210, 123, 22, 102, 65, 203, 193, 128,
    132, 144, 253, 134, 124, 48, 141, 54, 60, 224, 226, 246, 19, 148, 29,
    91, 173, 243, 244, 88, 208, 7, 198, 103, 217, 43, 199, 24, 58, 160, 221,
    151, 89, 214, 69, 82, 112, 115, 127, 155, 99, 180, 164, 172, 27, 109,
    21, 185, 187, 145, 140, 96, 201, 137, 138, 0, 6, 142, 34, 251, 8, 72,
    11, 75, 205, 70, 57, 174, 184, 204, 149, 163, 111, 59, 186, 79, 53, 42,
    52, 110, 189, 104, 15, 196, 4, 188, 117, 36, 158, 197, 78, 61, 154, 242,
    231, 223, 32, 17, 183, 56, 143, 233, 16, 169, 165, 245, 23, 101, 116,
    38, 84, 135, 234, 133, 147, 46, 131, 67, 2, 136, 50, 167, 86, 118, 1,
    9, 202, 73, 12, 191, 235, 153, 152, 238, 213, 222, 68, 28, 239, 93, 215,
    176, 98, 126, 159, 13, 250, 94, 87, 113, 49, 31, 83, 232, 229, 108, 240,
    170, 175, 100, 44, 230, 255, 114, 249, 40, 178, 47, 77, 252, 105, 179,
    146, 182, 171, 157, 212, 106, 92, 90,
]

INIT = [248, 142, 163, 165, 248, 3, 71, 246, 9, 67, 203, 73, 195, 2, 192, 201, 203, 136]
BLOCKSIZE = 8

# Known 2-block collision.
M1_HEX = "b8d80a072362cc220000000000800000"
M2_HEX = "b8d80a072362cca20000000000000000"


def blocks(data: bytes) -> Iterable[bytes]:
    for i in range(0, len(data), BLOCKSIZE):
        yield data[i : i + BLOCKSIZE]


def permute(state: list[int]) -> list[int]:
    out = [0] * len(state)
    for bit in range(8):
        for idx, value in enumerate(state):
            out[PBOXES[bit][idx]] |= value & (1 << bit)
    return out


def H(msg: bytes) -> bytes:
    assert len(msg) % BLOCKSIZE == 0
    state = INIT[:]
    for block in blocks(msg):
        for i, c in enumerate(block):
            state[i] ^= c
        for _ in range(8):
            state = permute(state)
            state = [SBOX[x] for x in state]
    return bytes(state)


def verify_collision() -> tuple[bytes, bytes, bytes]:
    m1 = bytes.fromhex(M1_HEX)
    m2 = bytes.fromhex(M2_HEX)
    h1 = H(m1)
    h2 = H(m2)

    assert m1 != m2, "messages must differ"
    assert h1 == h2, "collision check failed"
    return m1, m2, h1


def run_local(chal_path: str, python_bin: str = "python3") -> None:
    m1, m2, digest = verify_collision()
    print(f"[+] local collision verified", flush=True)
    print(f"[+] m1 = {m1.hex()}", flush=True)
    print(f"[+] m2 = {m2.hex()}", flush=True)
    print(f"[+] H(m1) = H(m2) = {digest.hex()}", flush=True)

    payload = f"{m1.hex()}\n{m2.hex()}\n".encode()
    import os
    env = os.environ.copy()
    env.setdefault("FLAG", "HTB{local_test_flag}")
    proc = subprocess.run(
        [python_bin, chal_path],
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env=env,
    )
    print("[+] local process output:", flush=True)
    sys.stdout.buffer.write(proc.stdout)
    if proc.returncode != 0:
        print(f"[!] local process exited with code {proc.returncode}", flush=True)


def recv_all(sock: socket.socket) -> bytes:
    chunks = []
    sock.settimeout(2.0)
    while True:
        try:
            data = sock.recv(4096)
        except socket.timeout:
            break
        if not data:
            break
        chunks.append(data)
    return b"".join(chunks)


def run_remote(host: str, port: int) -> None:
    m1, m2, digest = verify_collision()
    print(f"[+] remote collision verified", flush=True)
    print(f"[+] m1 = {m1.hex()}", flush=True)
    print(f"[+] m2 = {m2.hex()}", flush=True)
    print(f"[+] H(m1) = H(m2) = {digest.hex()}", flush=True)

    with socket.create_connection((host, port), timeout=10) as sock:
        banner = recv_all(sock)
        if banner:
            print("[+] banner:", flush=True)
            print(banner.decode(errors="replace"), end="", flush=True)

        sock.sendall(m1.hex().encode() + b"\n")
        sock.sendall(m2.hex().encode() + b"\n")

        response = recv_all(sock)
        print("[+] server response:", flush=True)
        print(response.decode(errors="replace"), end="", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Solver for the CryptoHack/HTB spongebob challenge")
    parser.add_argument("--local", metavar="PATH", help="run against a local challenge script")
    parser.add_argument("--python", default="python3", help="python interpreter for --local")
    parser.add_argument("--remote", action="store_true", help="run against the remote service")
    parser.add_argument("--host", default="archive.cryptohack.org")
    parser.add_argument("--port", type=int, default=37916)
    args = parser.parse_args()

    if not args.local and not args.remote:
        parser.error("choose at least one of --local or --remote")

    if args.local:
        run_local(args.local, args.python)

    if args.remote:
        run_remote(args.host, args.port)


if __name__ == "__main__":
    main()
