#!/usr/bin/env python3
import argparse
import builtins
import contextlib
import importlib.util
import io
import os
import socket
import subprocess
import sys
from pathlib import Path

CHALLENGE_PATH = Path('/mnt/data/chaos/chaos-zh3r0-ctf-v2/files/challenge_69e48fbabc70494136f3160b46f79ae4.py')
HOST = 'archive.cryptohack.org'
PORT = 18948

# Initial chaining values from the challenge
X0 = 0x0124fdce
Y0 = 0x89ab57ea
Z0 = 0xba89370a
U0 = 0xfedc45ef


def rep_nibble(n: int) -> int:
    """Repeat a nibble four times: 0xb -> 0xbbbb."""
    n &= 0xF
    return int(f"{n:x}" * 4, 16)


def rotl4(n: int, r: int = 2) -> int:
    n &= 0xF
    return ((n << r) & 0xF) | (n >> (4 - r))


def words_to_hex(words):
    return ''.join(f'{w:08x}' for w in words)


def derive_collision_words():
    """
    Derive the published collision instead of hardcoding it.

    Ý tưởng:
      Family 1: low 16 bits = 0   -> các tích bị triệt tiêu
      Family 2: high 16 bits = ffff -> các tích cũng bị triệt tiêu

    Sau đó chọn repeated nibble để phần rotate/xor khớp nhau.
    """
    p = 0xB
    q = rotl4(p, 2)  # 0xE

    P = rep_nibble(p)        # 0xbbbb
    Q = rep_nibble(q)        # 0xeeee
    P2 = rep_nibble(p ^ 0xF) # 0x4444
    Q2 = rep_nibble(q ^ 0xF) # 0x1111

    m1_words = [
        (P << 16) ^ X0,
        (Q << 16) ^ Y0,
        (Q << 16) ^ Z0,
        (P << 16) ^ U0,
    ]
    m2_words = [
        (0xFFFF0000 | P2) ^ X0,
        (0xFFFF0000 | Q2) ^ Y0,
        (0xFFFF0000 | Q2) ^ Z0,
        (0xFFFF0000 | P2) ^ U0,
    ]
    return m1_words, m2_words


def load_challenge_hash(challenge_path: Path):
    # challenge đọc FLAG khi import và còn chạy interactive block ở cuối file
    os.environ.setdefault('FLAG', 'flag{dummy}')
    spec = importlib.util.spec_from_file_location('chaos_challenge', str(challenge_path))
    mod = importlib.util.module_from_spec(spec)

    old_input = builtins.input
    builtins.input = lambda *args, **kwargs: ''
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            spec.loader.exec_module(mod)
    finally:
        builtins.input = old_input
    return mod.hash


def verify_locally(challenge_path: Path, m1_hex: str, m2_hex: str):
    hash_fn = load_challenge_hash(challenge_path)
    h1 = hash_fn(bytes.fromhex(m1_hex))
    h2 = hash_fn(bytes.fromhex(m2_hex))
    if h1 != h2:
        raise RuntimeError('Collision verification failed')
    if m1_hex == m2_hex:
        raise RuntimeError('Messages are equal, invalid collision')
    return h1.hex()


def run_local_binary(challenge_path: Path, m1_hex: str, m2_hex: str):
    env = os.environ.copy()
    env['FLAG'] = 'flag{local_test}'
    proc = subprocess.run(
        [sys.executable, str(challenge_path)],
        input=f'{m1_hex}\n{m2_hex}\n'.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
    return proc.stdout.decode(errors='replace'), proc.stderr.decode(errors='replace'), proc.returncode


def solve_remote(host: str, port: int, m1_hex: str, m2_hex: str):
    with socket.create_connection((host, port), timeout=10) as s:
        data = b''
        while b'input first string to hash : ' not in data:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        s.sendall(m1_hex.encode() + b'\n')

        while b'input second string to hash : ' not in data:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        s.sendall(m2_hex.encode() + b'\n')

        out = data
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            out += chunk
        return out.decode(errors='replace')


def main():
    parser = argparse.ArgumentParser(description='Solver for the CryptoHack archive challenge')
    parser.add_argument('--challenge', type=Path, default=CHALLENGE_PATH, help='Path to challenge python file')
    parser.add_argument('--remote', action='store_true', help='Submit the collision to the remote service')
    parser.add_argument('--host', default=HOST)
    parser.add_argument('--port', type=int, default=PORT)
    parser.add_argument('--no-local-check', action='store_true', help='Skip local hash verification')
    parser.add_argument('--run-local-binary', action='store_true', help='Run the original challenge script locally')
    args = parser.parse_args()

    m1_words, m2_words = derive_collision_words()
    m1_hex = words_to_hex(m1_words)
    m2_hex = words_to_hex(m2_words)

    print('[+] m1 =', m1_hex)
    print('[+] m2 =', m2_hex)

    if not args.no_local_check:
        digest = verify_locally(args.challenge, m1_hex, m2_hex)
        print('[+] hash(m1) = hash(m2) =', digest)

    if args.run_local_binary:
        stdout, stderr, code = run_local_binary(args.challenge, m1_hex, m2_hex)
        print('[+] local challenge output:')
        print(stdout, end='')
        if stderr:
            print('[!] stderr:')
            print(stderr, end='')
        print(f'[+] return code: {code}')

    if args.remote:
        print(f'[+] connecting to {args.host}:{args.port} ...')
        output = solve_remote(args.host, args.port, m1_hex, m2_hex)
        print('[+] remote output:')
        print(output, end='')


if __name__ == '__main__':
    main()
