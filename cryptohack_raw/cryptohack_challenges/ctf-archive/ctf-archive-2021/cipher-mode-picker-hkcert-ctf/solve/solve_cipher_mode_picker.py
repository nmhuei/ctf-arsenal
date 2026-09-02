#!/usr/bin/env python3
import argparse
import os
import re
import socket
import subprocess
import sys

FLAG_LEN = 80
HEX_RE = re.compile(r"[0-9a-fA-F]{32,}")


def extract_hex(line: bytes) -> bytes:
    text = line.decode(errors="replace").strip()
    matches = HEX_RE.findall(text)
    if not matches:
        raise RuntimeError(f"could not parse ciphertext from line: {text!r}")
    return bytes.fromhex(matches[-1])


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def recover(query):
    # CFB encryption of all-zero plaintext gives:
    #   C1 = AES(IV), C2 = AES(C1), ...
    # which is exactly the OFB keystream.
    ofb_keystream = query("cfb data " + "00" * FLAG_LEN)
    ofb_flag_ct = query("ofb flag")
    return xor(ofb_keystream, ofb_flag_ct)


def solve_remote(host: str, port: int):
    sock = socket.create_connection((host, port), timeout=15)
    f = sock.makefile("rwb", buffering=0)

    def query(cmd: str) -> bytes:
        f.write(cmd.encode() + b"\n")
        line = f.readline()
        if not line:
            raise RuntimeError("remote closed the connection")
        return extract_hex(line)

    flag = recover(query)
    print(flag.decode(errors="replace"))


def solve_local(chall_path: str):
    local_flag = ("hkcert21{" + "LOCAL_TEST_" + "A" * 59 + "}").encode()
    assert len(local_flag) == FLAG_LEN
    env = os.environ.copy()
    env["FLAG"] = local_flag.decode()
    p = subprocess.Popen(
        [sys.executable, chall_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    def query(cmd: str) -> bytes:
        assert p.stdin is not None and p.stdout is not None
        p.stdin.write(cmd.encode() + b"\n")
        p.stdin.flush()
        line = p.stdout.readline()
        if not line:
            err = p.stderr.read().decode(errors="replace") if p.stderr else ""
            raise RuntimeError("local challenge produced no output\n" + err)
        return extract_hex(line)

    flag = recover(query)
    p.kill()
    print(flag.decode(errors="replace"))
    print("local_ok =", flag == local_flag)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", metavar="CHALL.py", help="run against a local challenge file")
    ap.add_argument("--host", default="archive.cryptohack.org")
    ap.add_argument("--port", type=int, default=2951)
    args = ap.parse_args()
    if args.local:
        solve_local(args.local)
    else:
        solve_remote(args.host, args.port)


if __name__ == "__main__":
    main()
