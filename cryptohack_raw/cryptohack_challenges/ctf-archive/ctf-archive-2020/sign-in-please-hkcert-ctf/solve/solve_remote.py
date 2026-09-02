#!/usr/bin/env python3
import base64
import hashlib
import re
import socket
import sys

HOST = "archive.cryptohack.org"
PORT = 1024
TIMEOUT = 10.0
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
RAINBOW_SALT = bytes([0, 160, 2, 128])
RAINBOW_SALT_B64 = base64.b64encode(RAINBOW_SALT).decode()
INT_MASK = 0xFFFFFFFF
K = [
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2,
]


class Tube:
    def __init__(self, host: str, port: int):
        self.sock = socket.create_connection((host, port), timeout=TIMEOUT)
        self.sock.settimeout(TIMEOUT)
        self.buf = b""

    def recv_until(self, token: bytes) -> bytes:
        while token not in self.buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise EOFError(f"connection closed while waiting for {token!r}")
            self.buf += chunk
        idx = self.buf.index(token) + len(token)
        out, self.buf = self.buf[:idx], self.buf[idx:]
        return out

    def recv_line(self) -> bytes:
        return self.recv_until(b"\n")

    def recv_some(self) -> bytes:
        chunks = [self.buf]
        self.buf = b""
        self.sock.settimeout(1.0)
        try:
            while True:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
        except socket.timeout:
            pass
        finally:
            self.sock.settimeout(TIMEOUT)
        return b"".join(chunks)

    def sendline(self, data) -> None:
        if isinstance(data, str):
            data = data.encode()
        self.sock.sendall(data + b"\n")

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass


def rotr(x: int, n: int) -> int:
    return ((x >> n) | ((x << (32 - n)) & INT_MASK)) & INT_MASK


def sha256_compress_one_block(state, block: bytes):
    assert len(block) == 64
    w = [0] * 64
    for i in range(16):
        w[i] = int.from_bytes(block[4 * i:4 * (i + 1)], "big")
    for i in range(16, 64):
        s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
        s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
        w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & INT_MASK

    a, b, c, d, e, f, g, h = state
    for i in range(64):
        s1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)
        ch = (e & f) ^ ((~e) & g)
        temp1 = (h + s1 + ch + K[i] + w[i]) & INT_MASK
        s0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)
        maj = (a & b) ^ (a & c) ^ (b & c)
        temp2 = (s0 + maj) & INT_MASK
        h, g, f, e, d, c, b, a = g, f, e, (d + temp1) & INT_MASK, c, b, a, (temp1 + temp2) & INT_MASK

    return [
        (state[0] + a) & INT_MASK,
        (state[1] + b) & INT_MASK,
        (state[2] + c) & INT_MASK,
        (state[3] + d) & INT_MASK,
        (state[4] + e) & INT_MASK,
        (state[5] + f) & INT_MASK,
        (state[6] + g) & INT_MASK,
        (state[7] + h) & INT_MASK,
    ]


def state_to_hex(state) -> str:
    return "".join(f"{word:08x}" for word in state)


def hex_to_state(digest: str):
    return [int(digest[i:i + 8], 16) for i in range(0, 64, 8)]


def pair_block(a: str, b: str) -> bytes:
    return a.encode() + b.encode() + b"\x80" + b"\x00" * 59 + b"\x02\x10"


def spy_hash(conn: Tube, pbox, salt_b64: str) -> str:
    conn.recv_until(b"[cmd] ")
    conn.sendline("spy")
    conn.recv_until(b"[pbox] ")
    conn.sendline(str(pbox))
    conn.recv_until(b"[salt] ")
    conn.sendline(salt_b64)
    data = conn.recv_until(b"[hash] ") + conn.recv_line()
    m = re.search(rb"\[hash\] ([0-9a-f]{64})", data)
    if not m:
        raise RuntimeError(f"unexpected spy output: {data!r}")
    return m.group(1).decode()


def parse_auth_challenge(conn: Tube):
    conn.recv_until(b"[cmd] ")
    conn.sendline("auth")
    data = conn.recv_until(b"[hash] ")
    text = data.decode(errors="replace")

    pbox_match = re.search(r"\[pbox\] (\[[^\n]+\])", text)
    salt_match = re.search(r"\[salt\] ([A-Za-z0-9+/=]+)", text)
    if not pbox_match or not salt_match:
        raise RuntimeError(f"unexpected auth challenge: {text!r}")

    pbox = [int(x) for x in re.findall(r"-?\d+", pbox_match.group(1))]
    salt_b64 = salt_match.group(1)
    return pbox, base64.b64decode(salt_b64)


def permutate(payload: bytes, pbox) -> bytes:
    return bytes(payload[x] for x in pbox)


def recover_password(conn: Tube) -> str:
    first = spy_hash(conn, list(range(20)), RAINBOW_SALT_B64)
    first_state = hex_to_state(first)

    rainbow = {}
    for a in ALPHABET:
        for b in ALPHABET:
            rainbow[state_to_hex(sha256_compress_one_block(first_state, pair_block(a, b)))] = a + b

    recovered = []
    for i in range(8):
        pbox = list(range(20)) + [19] + [16] * 42 + [17] + [2 * i, 2 * i + 1]
        digest = spy_hash(conn, pbox, RAINBOW_SALT_B64)
        pair = rainbow.get(digest)
        if pair is None:
            raise RuntimeError(f"failed to recover pair {i}: {digest}")
        recovered.append(pair)
    return "".join(recovered)


def main() -> int:
    host = sys.argv[1] if len(sys.argv) >= 2 else HOST
    port = int(sys.argv[2]) if len(sys.argv) >= 3 else PORT

    print(f"[+] connecting to {host}:{port}")
    conn = Tube(host, port)
    try:
        password = recover_password(conn)
        print(f"[+] recovered password = {password}")

        pbox, salt = parse_auth_challenge(conn)
        print(f"[+] auth pbox = {pbox}")
        print(f"[+] auth salt = {base64.b64encode(salt).decode()}")

        digest = hashlib.sha256(permutate(password.encode() + salt, pbox)).hexdigest()
        conn.sendline(digest)

        out = conn.recv_some().decode(errors="replace")
        print(out, end="")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
