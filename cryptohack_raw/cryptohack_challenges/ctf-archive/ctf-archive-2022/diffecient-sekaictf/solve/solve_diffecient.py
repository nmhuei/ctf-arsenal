#!/usr/bin/env python3
import socket
import struct
import subprocess
import sys
import os
from pathlib import Path

MASK = (1 << 32) - 1
M = 2**32 - 5
C1 = 0xcc9e2d51
C2 = 0x1b873593
INV_C1 = pow(C1, -1, 1 << 32)
INV_C2 = pow(C2, -1, 1 << 32)


def rotr32(x, r):
    return ((x >> r) | (x << (32 - r))) & MASK


def inv_murmur_block_mix(mixed):
    """Return a 4-byte little-endian block whose MurmurHash3 block mix is `mixed`."""
    x = (mixed * INV_C2) & MASK
    x = rotr32(x, 15)
    k = (x * INV_C1) & MASK
    return struct.pack('<I', k)


def make_keys():
    # 32-byte prefix already satisfies admin regex: lowercase, uppercase, digit, special.
    prefix = b'Aa0!' * 8

    # Murmur block update is h <- L(h xor a), with L(x)=rotl(x,13)*5+c.
    # Since L(x xor 0x40000) == L(x) xor 0x80000000 for every x,
    # the two 2-block suffixes below collide for every seed.
    a = 0
    b = 0
    sample = prefix + inv_murmur_block_mix(a) + inv_murmur_block_mix(b)
    admin  = prefix + inv_murmur_block_mix(a ^ 0x40000) + inv_murmur_block_mix(b ^ 0x80000000)
    assert sample != admin
    return sample, admin


def recv_until(sock, marker, timeout=20):
    sock.settimeout(timeout)
    data = b''
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data


def solve_remote(host, port):
    sample, admin = make_keys()
    with socket.create_connection((host, int(port)), timeout=20) as s:
        out = recv_until(s, b'Enter API option:\n')
        s.sendall(b'2\n')
        out += recv_until(s, b'Enter key in hex\n')
        s.sendall(sample.hex().encode() + b'\n')
        out += recv_until(s, b'Enter API option:\n')
        s.sendall(b'3\n')
        out += recv_until(s, b'Enter key in hex\n')
        s.sendall(admin.hex().encode() + b'\n')
        # Read remaining output; server keeps loop open after printing flag, so use short timeout.
        s.settimeout(3)
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break
                out += chunk
            except socket.timeout:
                break
    print(out.decode(errors='replace'))


def solve_local(source_path):
    sample, admin = make_keys()
    env = os.environ.copy()
    env.setdefault('FLAG', 'SEKAI{local_test_flag}')
    payload = b'2\n' + sample.hex().encode() + b'\n3\n' + admin.hex().encode() + b'\n4\n'
    p = subprocess.run([sys.executable, '-u', source_path], input=payload,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, timeout=60)
    print(p.stdout.decode(errors='replace'))


def selftest_hashes():
    try:
        import mmh3
    except ImportError:
        print('[!] mmh3 not installed; skipping hash self-test')
        return
    sample, admin = make_keys()
    for seed in range(47):
        hs = mmh3.hash(sample, seed) % M
        ha = mmh3.hash(admin, seed) % M
        assert hs == ha, (seed, hs, ha)
    print('[+] all 47 seeded mmh3 digests collide')
    print('[+] sample hex =', sample.hex())
    print('[+] admin  hex =', admin.hex())


if __name__ == '__main__':
    if len(sys.argv) == 1:
        selftest_hashes()
        print('\nUsage:')
        print('  python3 solve_diffecient.py local /path/to/source.py')
        print('  python3 solve_diffecient.py remote archive.cryptohack.org 29201')
    elif sys.argv[1] == 'local':
        selftest_hashes()
        solve_local(sys.argv[2])
    elif sys.argv[1] == 'remote':
        solve_remote(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit('unknown mode')
