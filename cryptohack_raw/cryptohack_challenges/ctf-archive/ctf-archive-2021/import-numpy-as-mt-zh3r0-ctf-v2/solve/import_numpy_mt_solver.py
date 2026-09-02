#!/usr/bin/env python3
import argparse
import os
import socket
import subprocess
import sys

from numpy import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pyboolector import Boolector, BtorOption

M = 397
U = 0x80000000
L = 0x7fffffff
A = 0x9908B0DF
C = 1812433253


def words_from_iv(iv: bytes):
    return [int.from_bytes(iv[i:i + 4], "little") for i in range(0, 16, 4)]


def recover_seed(outputs):
    """Recover the 32-bit NumPy MT19937 seed from the first 4 uint32 outputs."""
    b = Boolector()
    b.Set_opt(BtorOption.BTOR_OPT_MODEL_GEN, 1)
    sort = b.BitVecSort(32)

    def bv(x):
        return b.Const(x & 0xffffffff, 32)

    def shr(x, n):
        return b.Srl(x, b.Const(n, 32))

    def temper(y):
        y = y ^ shr(y, 11)
        y = y ^ ((y << b.Const(7, 32)) & bv(0x9D2C5680))
        y = y ^ ((y << b.Const(15, 32)) & bv(0xEFC60000))
        y = y ^ shr(y, 18)
        return y

    # NumPy/MT19937 init_genrand recurrence. Only state[0..400] are needed
    # to express the first 4 outputs after the initial twist.
    st = [None] * 401
    st[0] = b.Var(sort, "seed")
    for i in range(1, 401):
        st[i] = bv(C) * (st[i - 1] ^ shr(st[i - 1], 30)) + bv(i)

    for i, out in enumerate(outputs):
        y = (st[i] & bv(U)) | (st[i + 1] & bv(L))
        mag = b.Cond(b.Eq(y & bv(1), bv(1)), bv(A), bv(0))
        twisted = st[i + M] ^ shr(y, 1) ^ mag
        b.Assert(b.Eq(temper(twisted), bv(out)))

    if b.Sat() != b.SAT:
        raise RuntimeError("seed recovery failed")
    return int(st[0].assignment, 2)


def iv_key_from_seed(seed: int):
    random.seed(seed)
    return random.bytes(16), random.bytes(16)


def decrypt_layer(blob: bytes):
    iv, ct = blob[:16], blob[16:]
    seed = recover_seed(words_from_iv(iv))
    real_iv, key = iv_key_from_seed(seed)
    if real_iv != iv:
        raise RuntimeError("recovered seed did not reproduce IV")
    pt = AES.new(key, AES.MODE_CBC, iv=iv).decrypt(ct)
    return seed, pt


def solve_hex(hex_ciphertext: str):
    blob = bytes.fromhex(hex_ciphertext.strip())
    outer_seed, inner_blob = decrypt_layer(blob)
    inner_seed, padded_flag = decrypt_layer(inner_blob)
    return outer_seed, inner_seed, unpad(padded_flag, 16)


def get_remote(host: str, port: int):
    with socket.create_connection((host, port), timeout=20) as s:
        chunks = []
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
            if b"\n" in chunk:
                break
    return b"".join(chunks).decode().strip()


def get_local(challenge_py: str, flag: str):
    env = os.environ.copy()
    env["FLAG"] = flag
    return subprocess.check_output([sys.executable, challenge_py], env=env, text=True).strip()


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--hex", help="ciphertext hex")
    src.add_argument("--remote", nargs=2, metavar=("HOST", "PORT"))
    src.add_argument("--local", metavar="CHALLENGE_PY")
    ap.add_argument("--flag", default="zh3r0{local_test_flag}", help="FLAG value for --local")
    args = ap.parse_args()

    if args.remote:
        hx = get_remote(args.remote[0], int(args.remote[1]))
        print("ciphertext =", hx, file=sys.stderr)
    elif args.local:
        hx = get_local(args.local, args.flag)
        print("ciphertext =", hx, file=sys.stderr)
    elif args.hex:
        hx = args.hex
    else:
        hx = sys.stdin.read().strip()

    outer_seed, inner_seed, flag = solve_hex(hx)
    print(f"outer_seed = {outer_seed:#010x}")
    print(f"inner_seed = {inner_seed:#010x}")
    print(flag.decode(errors="replace"))


if __name__ == "__main__":
    main()
