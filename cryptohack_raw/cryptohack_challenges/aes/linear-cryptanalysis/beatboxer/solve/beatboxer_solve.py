#!/usr/bin/env python3
"""
Solver for CryptoHack 'Beatboxer'.

Usage:
  python3 beatboxer_solve.py --local /path/to/13406_d7fa07291de630ace1055895f9ae208b.py
  python3 beatboxer_solve.py --remote socket.cryptohack.org 13406 --challenge /path/to/13406_d7fa07291de630ace1055895f9ae208b.py
"""
import argparse
import importlib.util
import json
import socket
import sys
import types
from pathlib import Path

N = 128


def import_challenge(path: str):
    # The challenge imports CryptoHack's utils.listener and starts a server at import time.
    # Stub the listener so importing the AES/Challenge classes is safe locally.
    utils = types.ModuleType("utils")
    utils.listener = types.SimpleNamespace(start_server=lambda *a, **kw: None)
    sys.modules["utils"] = utils
    spec = importlib.util.spec_from_file_location("beatboxer_chal", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def b2i(b: bytes) -> int:
    return int.from_bytes(b, "little")


def i2b(x: int) -> bytes:
    return x.to_bytes(16, "little")


def build_linear_tools(AES):
    # With the affine S-box, for every key k: E_k(P) = L(P) xor offset(k).
    # Derive L from the zero key, then invert L by Gaussian elimination.
    aes0 = AES(bytes(16))
    base = b2i(aes0.encrypt(bytes(16)))

    cols = []
    for bit in range(N):
        cols.append(b2i(aes0.encrypt(i2b(1 << bit))) ^ base)

    rows0 = []
    for out_bit in range(N):
        row = 0
        mask = 1 << out_bit
        for in_bit, col in enumerate(cols):
            if col & mask:
                row |= 1 << in_bit
        rows0.append(row)

    def apply_L(block: bytes) -> int:
        x = b2i(block)
        y = 0
        for bit, col in enumerate(cols):
            if (x >> bit) & 1:
                y ^= col
        return y

    def invert_L(y: int) -> int:
        rows = rows0[:]
        rhs = [(y >> i) & 1 for i in range(N)]
        where = [-1] * N
        r = 0
        for col in range(N):
            bit = 1 << col
            piv = next((i for i in range(r, N) if rows[i] & bit), None)
            if piv is None:
                continue
            rows[r], rows[piv] = rows[piv], rows[r]
            rhs[r], rhs[piv] = rhs[piv], rhs[r]
            for i in range(N):
                if i != r and (rows[i] & bit):
                    rows[i] ^= rows[r]
                    rhs[i] ^= rhs[r]
            where[col] = r
            r += 1
        if r != N:
            raise RuntimeError("linear layer was not invertible")
        x = 0
        for col, row_index in enumerate(where):
            if rhs[row_index]:
                x |= 1 << col
        return x

    return apply_L, invert_L


def pkcs7_unpad(data: bytes) -> bytes:
    if data and 1 <= data[-1] <= 16 and data.endswith(bytes([data[-1]]) * data[-1]):
        return data[:-data[-1]]
    return data


def decrypt_flag(enc_flag: bytes, known_plain: bytes, known_cipher: bytes, apply_L, invert_L) -> bytes:
    offset = b2i(known_cipher) ^ apply_L(known_plain)
    plaintext = b""
    for i in range(0, len(enc_flag), 16):
        plaintext += i2b(invert_L(b2i(enc_flag[i:i + 16]) ^ offset))
    return pkcs7_unpad(plaintext)


def local_solve(chal, apply_L, invert_L) -> bytes:
    service = chal.Challenge()
    known_plain = bytes(16)
    r1 = service.challenge({"option": "encrypt_message", "message": known_plain.hex()})
    r2 = service.challenge({"option": "encrypt_flag"})
    return decrypt_flag(bytes.fromhex(r2["encrypted_flag"]), known_plain, bytes.fromhex(r1["encrypted_message"]), apply_L, invert_L)


def recv_json_line(sock: socket.socket) -> dict:
    buf = b""
    while True:
        chunk = sock.recv(1)
        if not chunk:
            raise EOFError("socket closed before a JSON response arrived")
        if chunk == b"\n":
            line = buf.decode(errors="replace").strip()
            if not line or not line.startswith("{"):
                buf = b""
                continue
            return json.loads(line)
        buf += chunk


def send_json(sock: socket.socket, obj: dict) -> dict:
    sock.sendall(json.dumps(obj).encode() + b"\n")
    return recv_json_line(sock)


def remote_solve(host: str, port: int, apply_L, invert_L) -> bytes:
    known_plain = bytes(16)
    with socket.create_connection((host, port), timeout=15) as s:
        s.settimeout(15)
        r1 = send_json(s, {"option": "encrypt_message", "message": known_plain.hex()})
        if "encrypted_message" not in r1:
            raise RuntimeError(f"unexpected encrypt_message response: {r1}")
        r2 = send_json(s, {"option": "encrypt_flag"})
        if "encrypted_flag" not in r2:
            raise RuntimeError(f"unexpected encrypt_flag response: {r2}")
    return decrypt_flag(bytes.fromhex(r2["encrypted_flag"]), known_plain, bytes.fromhex(r1["encrypted_message"]), apply_L, invert_L)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--challenge", default="../files/13406_d7fa07291de630ace1055895f9ae208b.py")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--remote", nargs=2, metavar=("HOST", "PORT"))
    args = parser.parse_args()

    if not Path(args.challenge).exists():
        raise SystemExit(f"challenge file not found: {args.challenge}")

    chal = import_challenge(args.challenge)
    sbox = chal.AES.sbox
    assert all(sbox[x ^ y] == (sbox[x] ^ sbox[y] ^ sbox[0]) for x in range(256) for y in range(256)), "S-box is not affine"
    apply_L, invert_L = build_linear_tools(chal.AES)

    if args.local:
        print(local_solve(chal, apply_L, invert_L).decode())
    if args.remote:
        host, port_s = args.remote
        print(remote_solve(host, int(port_s), apply_L, invert_L).decode())
    if not args.local and not args.remote:
        print("Run with --local and/or --remote HOST PORT")


if __name__ == "__main__":
    main()
