#!/usr/bin/env python3
import base64
import os
import socket
import subprocess
import sys
import time
from typing import Optional

# Ed25519 subgroup order
L = 2**252 + 27742317777372353535851937790883648493

IDENTITY = (1).to_bytes(32, "little")
ZERO32 = b"\x00" * 32
MAGIC_VK = IDENTITY
MAGIC_SIG = IDENTITY + ZERO32


def b64(x: bytes) -> bytes:
    return base64.b64encode(x)


def forge_same_message_sig(sig_b64: str) -> bytes:
    sig = base64.b64decode(sig_b64.strip())
    if len(sig) != 64:
        raise ValueError(f"expected 64-byte signature, got {len(sig)} bytes")
    R = sig[:32]
    S = int.from_bytes(sig[32:], "little")
    # Verification in the bundled python-ed25519/SUPERCOP ref code reduces S modulo L
    # and does not enforce canonical S, so S+L gives a distinct valid signature.
    S2 = S + L
    if S2 >= 1 << 256:
        raise ValueError("S+L does not fit in 32 bytes; retry challenge")
    return R + S2.to_bytes(32, "little")


class ProcIO:
    def __init__(self, argv):
        env = os.environ.copy()
        env.setdefault("FLAG", "LOCAL_FLAG{ed25519_magic_ok}")
        self.p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        self.buf = b""

    def recv_until(self, marker: bytes, timeout: float = 5.0) -> bytes:
        end = time.time() + timeout
        while marker not in self.buf:
            if time.time() > end:
                raise TimeoutError(f"timeout waiting for {marker!r}; buffer={self.buf!r}")
            ch = self.p.stdout.read(1)
            if not ch:
                raise EOFError(f"process closed; buffer={self.buf!r}")
            self.buf += ch
        i = self.buf.index(marker) + len(marker)
        out, self.buf = self.buf[:i], self.buf[i:]
        return out

    def sendline(self, data: bytes):
        self.p.stdin.write(data + b"\n")
        self.p.stdin.flush()

    def close(self):
        try:
            self.p.kill()
        except Exception:
            pass


class SockIO:
    def __init__(self, host: str, port: int):
        self.s = socket.create_connection((host, port), timeout=10)
        self.s.settimeout(10)
        self.buf = b""

    def recv_until(self, marker: bytes, timeout: float = 10.0) -> bytes:
        old = self.s.gettimeout()
        self.s.settimeout(timeout)
        try:
            while marker not in self.buf:
                data = self.s.recv(4096)
                if not data:
                    raise EOFError(f"socket closed; buffer={self.buf!r}")
                self.buf += data
            i = self.buf.index(marker) + len(marker)
            out, self.buf = self.buf[:i], self.buf[i:]
            return out
        finally:
            self.s.settimeout(old)

    def sendline(self, data: bytes):
        self.s.sendall(data + b"\n")

    def close(self):
        self.s.close()


def solve(io) -> str:
    transcript = b""
    transcript += io.recv_until(b"Signature:\n")
    line = io.recv_until(b"\n")
    sig_b64 = line.decode().strip()
    print(f"[+] received sig: {sig_b64}")
    forged = forge_same_message_sig(sig_b64)

    transcript += line
    transcript += io.recv_until(b"Enter new signature:\n")
    io.sendline(b64(forged))
    print(f"[+] sent forged level1 sig: {b64(forged).decode()}")

    transcript += io.recv_until(b"Enter verifying key:\n")
    io.sendline(b64(MAGIC_VK))
    print(f"[+] sent magic vk: {b64(MAGIC_VK).decode()}")

    transcript += io.recv_until(b"Enter signature:\n")
    io.sendline(b64(MAGIC_SIG))
    print(f"[+] sent magic sig: {b64(MAGIC_SIG).decode()}")

    # Read final line(s). It may be just flag or 'None' locally.
    out = b""
    try:
        while True:
            chunk = io.recv_until(b"\n", timeout=2.0)
            out += chunk
    except Exception:
        pass
    final = out.decode(errors="replace").strip()
    print("[+] final output:")
    print(final)
    return final


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "local":
        chal = sys.argv[2] if len(sys.argv) >= 3 else "/mnt/data/ed25519_magic/ed25519-magic-icc-athens/files/chal_b65423a084f6906fe9deb2480fff3ea9.py"
        io = ProcIO([sys.executable, chal])
    elif len(sys.argv) >= 4 and sys.argv[1] == "remote":
        io = SockIO(sys.argv[2], int(sys.argv[3]))
    else:
        print(f"Usage:\n  {sys.argv[0]} local [chal.py]\n  {sys.argv[0]} remote HOST PORT")
        sys.exit(1)
    try:
        solve(io)
    finally:
        io.close()


if __name__ == "__main__":
    main()
