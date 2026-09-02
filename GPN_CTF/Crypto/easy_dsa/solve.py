#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import socket
import sys
from hashlib import sha256
from typing import Callable

from Crypto.PublicKey import ECC
from fpylll import IntegerMatrix, LLL

CURVE = ECC.generate(curve="p521")._curve
G = CURVE.G
N = int(CURVE.order)
B = 2**256


def z_of(msg: bytes) -> int:
    # Same as challenge: sha256(message) as integer. The mask in the challenge has no effect for P-521.
    e = int.from_bytes(sha256(msg).digest())
    return e & ~(1 << N.bit_length())


def recover_privkey(sigs: list[tuple[int, int, int]], bound: int = B) -> int:
    """Recover d from signatures (r, s, z), exploiting nonce k < 2^256 on P-521."""
    m = len(sigs)
    t, u = [], []
    for r, s, z in sigs:
        inv_s = pow(s, -1, N)
        t.append((r * inv_s) % N)
        u.append((z * inv_s) % N)

    # L = { d*t + n*l }. Normalize by the last coordinate so we have a compact basis
    # with determinant n^(m-1), then solve CVP by Kannan embedding.
    inv_last = pow(t[-1], -1, N)
    a = [(t[i] * inv_last) % N for i in range(m - 1)]

    basis = []
    for i in range(m - 1):
        row = [0] * m
        row[i] = N
        basis.append(row)
    basis.append(a + [1])

    target = [(-x) % N for x in u]
    M = bound
    embedding = [row + [0] for row in basis]
    embedding.append(target + [M])

    A = IntegerMatrix.from_matrix(embedding)
    LLL.reduction(A, delta=0.99)

    for i in range(A.nrows):
        row = [int(A[i, j]) for j in range(A.ncols)]
        if abs(row[-1]) != M:
            continue
        # In the embedded vector, the first coordinates are +/- the small nonce vector.
        for sign in (1, -1):
            k0 = sign * row[0]
            if not (1 <= k0 < bound):
                continue
            r0, s0, z0 = sigs[0]
            d = ((s0 * k0 - z0) * pow(r0, -1, N)) % N
            ok = True
            for r, s, z in sigs:
                k = ((z + r * d) * pow(s, -1, N)) % N
                if not (1 <= k < bound):
                    ok = False
                    break
            if ok:
                return d
    raise RuntimeError("private key not recovered; collect more signatures")


def forge(d: int, msg: bytes, k: int = 1337) -> tuple[int, int]:
    z = z_of(msg)
    P = k * G
    r = int(P.x % N)
    s = (pow(k, -1, N) * (z + r * d)) % N
    assert 1 <= r < N and 1 <= s < N
    return r, s


def read_until(sock, marker: bytes) -> bytes:
    data = b""
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data


def remote_mode(host: str, port: int):
    s = socket.create_connection((host, port))
    buf = read_until(s, b"> ")
    print(buf.decode(errors="replace"), end="")

    sigs = []
    messages = [f"recipe-{i}".encode() for i in range(6)]
    for msg in messages:
        s.sendall(b"sign " + msg.hex().encode() + b"\n")
        out = read_until(s, b"> ")
        print(out.decode(errors="replace"), end="")
        m = re.search(rb"s1: (0x[0-9a-f]+)\s*s2: (0x[0-9a-f]+)", out, re.S)
        if not m:
            raise RuntimeError("could not parse signature")
        r = int(m.group(1), 16)
        sig_s = int(m.group(2), 16)
        sigs.append((r, sig_s, z_of(msg)))

    d = recover_privkey(sigs)
    new_msg = b"new unsigned recipe for flag"
    r, sig_s = forge(d, new_msg)

    s.sendall(b"flag please\n")
    out = read_until(s, b"recipe (hex): ")
    print(out.decode(errors="replace"), end="")
    s.sendall(new_msg.hex().encode() + b"\n")
    out = read_until(s, b"s1 (hex): ")
    print(out.decode(errors="replace"), end="")
    s.sendall(hex(r).encode() + b"\n")
    out = read_until(s, b"s2 (hex): ")
    print(out.decode(errors="replace"), end="")
    s.sendall(hex(sig_s).encode() + b"\n")
    out = s.recv(8192)
    print(out.decode(errors="replace"), end="")
    s.close()


def local_mode():
    import pexpect

    env = os.environ.copy()
    env.setdefault("FLAG", "flag{local_lattice_recovery_success}")
    child = pexpect.spawn(sys.executable, ["main.py"], cwd=os.path.dirname(__file__), env=env, encoding="utf-8", timeout=10)
    child.expect_exact("> ")

    sigs = []
    messages = [f"recipe-{i}".encode() for i in range(6)]
    for msg in messages:
        child.sendline("sign " + msg.hex())
        child.expect_exact("> ")
        out = child.before
        m = re.search(r"s1: (0x[0-9a-f]+)\s*s2: (0x[0-9a-f]+)", out, re.S)
        if not m:
            raise RuntimeError("could not parse local signature: " + out)
        r = int(m.group(1), 16)
        s = int(m.group(2), 16)
        sigs.append((r, s, z_of(msg)))

    d = recover_privkey(sigs)
    new_msg = b"new unsigned recipe for flag"
    r, s = forge(d, new_msg)

    child.sendline("flag please")
    child.expect_exact("recipe (hex): ")
    child.sendline(new_msg.hex())
    child.expect_exact("s1 (hex): ")
    child.sendline(hex(r))
    child.expect_exact("s2 (hex): ")
    child.sendline(hex(s))
    child.expect("Congratulations\. Here is your flag: .+")
    print(child.after)
    child.close()


if __name__ == "__main__":
    if len(sys.argv) == 3:
        remote_mode(sys.argv[1], int(sys.argv[2]))
    else:
        local_mode()
