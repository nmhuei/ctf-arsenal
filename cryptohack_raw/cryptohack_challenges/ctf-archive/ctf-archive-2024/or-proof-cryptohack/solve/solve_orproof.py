#!/usr/bin/env python3
import os
import re
import sys
import socket
import subprocess
import secrets
import select
import time

# Embedded params, so the remote solver works even when params.py is not in this folder.
p = 0x1ed344181da88cae8dc37a08feae447ba3da7f788d271953299e5f093df7aaca987c9f653ed7e43bad576cc5d22290f61f32680736be4144642f8bea6f5bf55ef
q = 0xf69a20c0ed4465746e1bd047f57223dd1ed3fbc46938ca994cf2f849efbd5654c3e4fb29f6bf21dd6abb662e911487b0f9934039b5f20a23217c5f537adfaaf7
g = 2

# Public constants from chal.py
W0 = 0x5a0f15a6a725003c3f65238d5f8ae4641f6bf07ebf349705b7f1feda2c2b051475e33f6747f4c8dc13cd63b9dd9f0d0dd87e27307ef262ba68d21a238be00e83
Y0 = 0x514c8f56336411e75d5fa8c5d30efccb825ada9f5bf3f6eb64b5045bacf6b8969690077c84bea95aab74c24131f900f83adf2bfe59b80c5a0d77e8a9601454e5
Y1 = 0x1ccda066cd9d99e0b3569699854db7c5cf8d0e0083c4af57d71bf520ea0386d67c4b8442476df42964e5ed627466db3da532f65a8ce8328ede1dd7b35b82ed617
CHAL_BOUND = 2**511


def modinv(x, m):
    return pow(x % m, -1, m)


def simulate_one(y, e=None, z=None):
    """Simulate Schnorr transcript: g^z = a*y^e."""
    if e is None:
        e = secrets.randbelow(CHAL_BOUND)
    if z is None:
        z = secrets.randbelow(q)
    a = (pow(g, z, p) * modinv(pow(y, e, p), p)) % p
    return a, e, z


class Tube:
    def __init__(self, argv=None, host=None, port=None):
        self.buf = b""
        if argv is not None:
            self.proc = subprocess.Popen(
                argv,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0,
            )
            self.sock = None
        else:
            self.sock = socket.create_connection((host, int(port)))
            self.proc = None

    def _read_one(self):
        if self.proc is not None:
            b = self.proc.stdout.read(1)
        else:
            b = self.sock.recv(1)
        if not b:
            raise EOFError(self.buf.decode(errors="ignore"))
        self.buf += b

    def recvuntil(self, token):
        token_b = token.encode()
        while token_b not in self.buf:
            self._read_one()
        idx = self.buf.index(token_b) + len(token_b)
        out, self.buf = self.buf[:idx], self.buf[idx:]
        return out.decode(errors="ignore")

    def recvall_available(self, timeout=0.5):
        end = time.time() + timeout
        while time.time() < end:
            if self.proc is not None:
                r, _, _ = select.select([self.proc.stdout], [], [], 0.05)
                if not r:
                    continue
                b = os.read(self.proc.stdout.fileno(), 4096)
            else:
                self.sock.setblocking(False)
                try:
                    b = self.sock.recv(4096)
                except BlockingIOError:
                    continue
                finally:
                    self.sock.setblocking(True)
            if not b:
                break
            self.buf += b
        out, self.buf = self.buf, b""
        return out.decode(errors="ignore")

    def sendline(self, x):
        data = (str(x) + "\n").encode()
        if self.proc is not None:
            self.proc.stdin.write(data)
            self.proc.stdin.flush()
        else:
            self.sock.sendall(data)


def find_int(text, label):
    m = re.search(rf"{re.escape(label)}\*?\s*=\s*(\d+)", text)
    if not m:
        raise ValueError(f"missing {label} in output:\n{text}")
    return int(m.group(1))


def extract_witness(transcript_text):
    e0 = find_int(transcript_text, "e0")
    e1 = find_int(transcript_text, "e1")
    z0 = find_int(transcript_text, "z0")
    z1 = find_int(transcript_text, "z1")

    e0s = find_int(transcript_text, "e0*")
    e1s = find_int(transcript_text, "e1*")
    z0s = find_int(transcript_text, "z0*")
    z1s = find_int(transcript_text, "z1*")

    # Same commitment a and two different challenges gives:
    # z - z' = (e - e') * w mod q
    candidates = []
    if e0 != e0s:
        candidates.append(((z0 - z0s) % q) * modinv(e0 - e0s, q) % q)
    if e1 != e1s:
        candidates.append(((z1 - z1s) % q) * modinv(e1 - e1s, q) % q)
    if not candidates:
        raise RuntimeError("rewind collision: both transcripts used the same challenge")
    return candidates[0]


def solve(io):
    # 1) Correctness. We know W0, so prove honestly for branch 0 and simulate branch 1.
    r0 = secrets.randbelow(q)
    a0 = pow(g, r0, p)
    a1, e1, z1 = simulate_one(Y1)

    io.recvuntil("a0:")
    io.sendline(a0)
    io.recvuntil("a1:")
    io.sendline(a1)

    out = io.recvuntil("e0:")
    s = find_int(out, "s")
    e0 = s ^ e1
    z0 = (r0 + e0 * W0) % q

    io.sendline(e0)
    io.recvuntil("e1:")
    io.sendline(e1)
    io.recvuntil("z0:")
    io.sendline(z0)
    io.recvuntil("z1:")
    io.sendline(z1)

    # 2) Special soundness. Extract witness from two accepting transcripts with same commitments.
    transcript_text = io.recvuntil("give me a witness!")
    witness = extract_witness(transcript_text)
    io.sendline(witness)

    # 3) SHVZK. For a fixed global challenge s, simulate both sides directly.
    out = io.recvuntil("a0:")
    yy0 = find_int(out, "y0")
    yy1 = find_int(out, "y1")
    s = find_int(out, "s")

    e0 = secrets.randbelow(CHAL_BOUND)
    e1 = s ^ e0
    a0, _, z0 = simulate_one(yy0, e0)
    a1, _, z1 = simulate_one(yy1, e1)

    io.sendline(a0)
    io.recvuntil("a1:")
    io.sendline(a1)
    io.recvuntil("e0:")
    io.sendline(e0)
    io.recvuntil("e1:")
    io.sendline(e1)
    io.recvuntil("z0:")
    io.sendline(z0)
    io.recvuntil("z1:")
    io.sendline(z1)

    return io.recvall_available(1.0)


def main():
    # Usage:
    #   python3 solve_orproof.py local ./chal.py
    #   python3 solve_orproof.py remote archive.cryptohack.org 11840
    if len(sys.argv) >= 2 and sys.argv[1] == "remote":
        host = sys.argv[2] if len(sys.argv) > 2 else "archive.cryptohack.org"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 11840
        io = Tube(host=host, port=port)
    else:
        chal = sys.argv[2] if len(sys.argv) > 2 else "chal.py"
        env = os.environ.copy()
        env.setdefault("FLAG", "crypto{LOCAL_TEST_FLAG}")
        # Let the challenge import local params.py.
        io = Tube(argv=[sys.executable, chal])
    print(solve(io), end="")


if __name__ == "__main__":
    main()
