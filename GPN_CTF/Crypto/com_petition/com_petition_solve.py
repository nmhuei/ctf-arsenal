#!/usr/bin/env python3
"""
Exploit for COMpetition.

Usage:
  Local proof:
    FLAG='flag{LOCAL_PROOF_FLAG}' python3 com_petition_solve.py --local ./main.py

  Remote:
    python3 com_petition_solve.py --host example.com --port 31337
"""
from __future__ import annotations

import argparse
import os
import re
import socket
import subprocess
import sys
from hashlib import sha256
from os import urandom
from typing import Dict, Tuple

WIN = {"rock": "paper", "paper": "scissors", "scissors": "rock"}
MOVES = [b"rock", b"paper", b"scissors"]


def make_commitment(round_no: int) -> Tuple[bytes, Dict[str, Tuple[bytes, bytes]]]:
    # The vulnerability: verify() hashes r1 + message + r2 with no length
    # binding. If this blob contains all three messages, the same digest can be
    # opened as rock/paper/scissors by choosing a different split point.
    blob = urandom(16) + round_no.to_bytes(4, "big") + b"|rock|paper|scissors|" + urandom(16)
    commitment = sha256(blob).digest()
    proofs: Dict[str, Tuple[bytes, bytes]] = {}
    for m in MOVES:
        i = blob.index(m)
        proofs[m.decode("ascii")] = (blob[:i], blob[i + len(m):])
    return commitment, proofs


class Conn:
    def sendline(self, line: str) -> None:
        raise NotImplementedError

    def recv_until(self, token: bytes) -> bytes:
        raise NotImplementedError

    def recv_regex(self, pattern: bytes) -> re.Match[bytes]:
        raise NotImplementedError

    def recv_rest(self) -> bytes:
        raise NotImplementedError

    def close(self) -> None:
        pass


class SocketConn(Conn):
    def __init__(self, host: str, port: int):
        self.s = socket.create_connection((host, port), timeout=10)
        self.s.settimeout(10)
        self.buf = b""

    def _read_more(self) -> None:
        chunk = self.s.recv(4096)
        if not chunk:
            raise EOFError("remote closed connection")
        self.buf += chunk

    def sendline(self, line: str) -> None:
        self.s.sendall(line.encode() + b"\n")

    def recv_until(self, token: bytes) -> bytes:
        while token not in self.buf:
            self._read_more()
        idx = self.buf.index(token) + len(token)
        out, self.buf = self.buf[:idx], self.buf[idx:]
        return out

    def recv_regex(self, pattern: bytes) -> re.Match[bytes]:
        rx = re.compile(pattern, re.S)
        while True:
            m = rx.search(self.buf)
            if m:
                self.buf = self.buf[m.end():]
                return m
            self._read_more()

    def recv_rest(self) -> bytes:
        self.s.settimeout(1)
        try:
            while True:
                chunk = self.s.recv(4096)
                if not chunk:
                    break
                self.buf += chunk
        except Exception:
            pass
        return self.buf

    def close(self) -> None:
        self.s.close()


class LocalConn(SocketConn):
    def __init__(self, main_py: str):
        # Use unbuffered mode so prompts without newline are emitted immediately.
        self.p = subprocess.Popen(
            [sys.executable, "-u", main_py],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env={**os.environ, "FLAG": os.environ.get("FLAG", "flag{LOCAL_PROOF_FLAG}")},
        )
        self.buf = b""
        self.s = None

    def _read_more(self) -> None:
        assert self.p.stdout is not None
        chunk = self.p.stdout.read(1)
        if not chunk:
            raise EOFError("local process exited")
        self.buf += chunk

    def sendline(self, line: str) -> None:
        assert self.p.stdin is not None
        self.p.stdin.write(line.encode() + b"\n")
        self.p.stdin.flush()

    def recv_rest(self) -> bytes:
        try:
            assert self.p.stdout is not None
            self.buf += self.p.stdout.read() or b""
        except Exception:
            pass
        return self.buf

    def close(self) -> None:
        try:
            self.p.kill()
        except Exception:
            pass


def solve(conn: Conn) -> str:
    transcript = []
    transcript.append(conn.recv_until(b"I want to play a game"))
    used = set()

    for round_no in range(100):
        transcript.append(conn.recv_until(b"Commitment (hex): "))
        commitment, proofs = make_commitment(round_no)
        if commitment in used:
            raise RuntimeError("unexpected duplicate commitment")
        used.add(commitment)
        conn.sendline(commitment.hex())

        m = conn.recv_regex(rb"I choose (rock|paper|scissors)\.")
        server_choice = m.group(1).decode("ascii")
        my_choice = WIN[server_choice]

        transcript.append(conn.recv_until(b"What did you choose? "))
        conn.sendline(my_choice)

        transcript.append(conn.recv_until(b"Proof (hex): "))
        r1, r2 = proofs[my_choice]
        conn.sendline(f"{r1.hex()} {r2.hex()}")

    final = conn.recv_rest().decode(errors="replace")
    match = re.search(r"flag\{[^\r\n}]*\}|[A-Z0-9_]+\{[^\r\n}]+\}", final)
    return match.group(0) if match else final.strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--local", metavar="MAIN_PY")
    g.add_argument("--host")
    ap.add_argument("--port", type=int)
    args = ap.parse_args()

    if args.local:
        conn = LocalConn(args.local)
    else:
        if args.port is None:
            ap.error("--port is required with --host")
        conn = SocketConn(args.host, args.port)

    try:
        print(solve(conn))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
