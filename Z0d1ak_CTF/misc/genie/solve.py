#!/usr/bin/env python3
"""
Solve script for z0d1akCTF 2026 Qualifiers / Misc / genie.

The service prints a 16-bit seed, then expects a compact JSON movie.
Derives the three live codewords for the authenticated gold counter,
submits a movie that jumps to floor 9, drives the echo state machine
with the recovered 9-symbol sequence, and prints the flag on WIN.
"""
from __future__ import annotations

import argparse
import json
import re
import socket
import ssl

DEFAULT_HOST = "genie-b8d42461bd1e.chals.z0d1ak.org"
DEFAULT_PORT = 1337
MASK16 = 0xFFFF

A_BUTTON = 0x10
START = 0x80

ECHO_SEQUENCE = [2, 0, 2, 1, 2, 2, 0, 2, 1]


def rol16(value: int, count: int) -> int:
    value &= MASK16
    return ((value << count) | (value >> (16 - count))) & MASK16


def session_key(seed: int) -> int:
    """ROM helper at 0x04a5."""
    return ((0x3D29 + rol16(seed ^ 0xA5C3, 7)) & MASK16) ^ 0x6B71


def gold_mac(gold: int, key: int) -> int:
    """ROM helper at 0x0578."""
    mixed = (0x6D2B + rol16(gold ^ key, 3)) & MASK16
    return rol16(mixed ^ rol16(key, 7), 5)


def codewords_for_gold(seed: int, gold: int = 5000) -> tuple[int, int, int]:
    key = session_key(seed)
    return gold, gold ^ key, gold_mac(gold, key)


def build_movie(seed: int, total_frames: int = 220) -> dict:
    joypad = [0] * total_frames
    codes: list[list[int]] = []

    gold0, gold1, gold2 = codewords_for_gold(seed)
    start_frame = 20
    codes.extend([
        [start_frame, 0xC100, gold0],
        [start_frame, 0xC102, gold1],
        [start_frame, 0xC104, gold2],
    ])
    joypad[start_frame] = START

    frame = 40
    for selector in ECHO_SEQUENCE:
        joypad[frame] = A_BUTTON
        codes.append([frame + 1, 0xC300, selector])
        frame += 12

    return {"version": 1, "seed": seed, "joypad": joypad, "codes": codes}


def recv_until(sock: ssl.SSLSocket, marker: bytes) -> bytes:
    data = b""
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data


def solve_remote(host: str, port: int, dump_movie: bool = False) -> str:
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=15) as raw:
        with ctx.wrap_socket(raw, server_hostname=host) as sock:
            sock.settimeout(15)
            banner = recv_until(sock, b"movie-json>")
            text = banner.decode("utf-8", "replace")
            print("BANNER:", text, end="")
            match = re.search(r"seed=(\d+)", text)
            if not match:
                raise RuntimeError(f"service did not print a seed:\n{text}")
            seed = int(match.group(1))
            movie = build_movie(seed)
            line = json.dumps(movie, separators=(",", ":"))
            print(f"movie bytes: {len(line)}")
            if dump_movie:
                print(line)
            sock.sendall(line.encode() + b"\n")
            response = b""
            while True:
                try:
                    chunk = sock.recv(4096)
                except socket.timeout:
                    break
                if not chunk:
                    break
                response += chunk
    result = response.decode("utf-8", "replace")
    print("RESPONSE:", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("host", nargs="?", default=DEFAULT_HOST)
    parser.add_argument("port", nargs="?", type=int, default=DEFAULT_PORT)
    parser.add_argument("--seed", type=int, help="print the movie for a known seed")
    parser.add_argument("--dump-movie", action="store_true")
    args = parser.parse_args()

    if args.seed is not None:
        print(json.dumps(build_movie(args.seed), separators=(",", ":")))
        return
    solve_remote(args.host, args.port, dump_movie=args.dump_movie)


if __name__ == "__main__":
    main()
