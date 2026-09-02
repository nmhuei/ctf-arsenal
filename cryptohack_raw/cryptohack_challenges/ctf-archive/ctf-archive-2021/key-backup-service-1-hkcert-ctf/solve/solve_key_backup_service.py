#!/usr/bin/env python3
import argparse
import itertools
import os
import socket
import subprocess
import sys

E = 17
M = 1 << 61
PROMPT = b'[cmd] '
DEFAULT_CHALL = './chall_bebddbec57df20f4a07fafc9ad2eacfd.py'

try:
    from Crypto.Cipher import AES as _AES
    def aes_cbc_decrypt(key, iv, ct):
        return _AES.new(key, _AES.MODE_CBC, iv).decrypt(ct)
except Exception:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    def aes_cbc_decrypt(key, iv, ct):
        dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
        return dec.update(ct) + dec.finalize()


def pkcs7_unpad(data, block=16):
    n = data[-1]
    if 1 <= n <= block and data.endswith(bytes([n]) * n):
        return data[:-n]
    return data


def iroot(n, k):
    if n in (0, 1):
        return n, True
    lo, hi = 0, 1 << ((n.bit_length() + k - 1) // k)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if pow(mid, k) <= n:
            lo = mid
        else:
            hi = mid
    return lo, pow(lo, k) == n


def crt(residues, moduli):
    x, m = residues[0], moduli[0]
    for a, n in zip(residues[1:], moduli[1:]):
        t = ((a - x) * pow(m, -1, n)) % n
        x += m * t
        m *= n
    return x, m


def recover_n_candidates(c):
    A = pow(M, E) - c
    candidates = []
    # p and q are both 512-bit with their top bit set, so n is in [2^1022, 2^1024).
    # With M=2^61, floor(M^17/n) is a small integer around 2^13..2^15.
    for k in range(1 << 12, 1 << 17):
        if A % k == 0:
            n = A // k
            if (1 << 1022) <= n < (1 << 1024) and pow(M, E, n) == c:
                candidates.append((k, n))
    return [n for k, n in sorted(candidates, reverse=True)]


class ProcConn:
    def __init__(self, path, flag):
        env = os.environ.copy()
        env['FLAG'] = flag
        self.p = subprocess.Popen(
            [sys.executable, path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

    def recv1(self):
        ch = self.p.stdout.read(1)
        if not ch:
            err = self.p.stderr.read().decode(errors='replace')
            raise EOFError('process ended: ' + err)
        return ch

    def read_until(self, token=PROMPT):
        data = b''
        while not data.endswith(token):
            data += self.recv1()
        return data

    def sendline(self, s):
        self.p.stdin.write(s.encode() + b'\n')
        self.p.stdin.flush()

    def close(self):
        try:
            self.p.kill()
        except Exception:
            pass


class SockConn:
    def __init__(self, host, port):
        self.s = socket.create_connection((host, int(port)), timeout=20)
        self.buf = b''

    def recv1(self):
        ch = self.s.recv(1)
        if not ch:
            raise EOFError('socket closed')
        return ch

    def read_until(self, token=PROMPT):
        while token not in self.buf:
            chunk = self.s.recv(4096)
            if not chunk:
                raise EOFError('socket closed')
            self.buf += chunk
        idx = self.buf.index(token) + len(token)
        out, self.buf = self.buf[:idx], self.buf[idx:]
        return out

    def sendline(self, s):
        self.s.sendall(s.encode() + b'\n')

    def close(self):
        self.s.close()


def cmd_getline(conn, s):
    conn.read_until(PROMPT)
    conn.sendline(s)
    line = b''
    while not line.endswith(b'\n'):
        line += conn.recv1()
    return line.strip().decode()


def exploit(conn):
    enc_flag_hex = cmd_getline(conn, 'flag')
    print('[+] encrypted flag:', enc_flag_hex)

    nlists, cs = [], []
    for i in range(5):
        conn.read_until(PROMPT)
        conn.sendline('pkey')

        c_known = int(cmd_getline(conn, 'send ' + hex(M)[2:]), 16)
        candidates = recover_n_candidates(c_known)
        if not candidates:
            raise RuntimeError('failed to recover modulus candidates')

        c_secret = int(cmd_getline(conn, 'backup'), 16)
        print(f'[+] sample {i}: modulus_candidates={len(candidates)}')
        nlists.append(candidates)
        cs.append(c_secret)

    for ns in itertools.product(*nlists):
        try:
            x, _ = crt(cs, list(ns))
        except ValueError:
            continue
        root, exact = iroot(x, E)
        if exact:
            master_secret = root.to_bytes(32, 'big')
            print('[+] master secret:', master_secret.hex())
            pt = aes_cbc_decrypt(master_secret, b'\0' * 16, bytes.fromhex(enc_flag_hex))
            return pkcs7_unpad(pt)

    raise RuntimeError('no modulus combination gave an exact 17th root')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='mode', required=True)
    lp = sub.add_parser('local')
    lp.add_argument('chall', nargs='?', default=DEFAULT_CHALL)
    lp.add_argument('--flag', default='hkcert21{local_test_flag_123}')
    rp = sub.add_parser('remote')
    rp.add_argument('host')
    rp.add_argument('port', type=int)
    args = ap.parse_args()

    if args.mode == 'local':
        conn = ProcConn(args.chall, args.flag)
    else:
        conn = SockConn(args.host, args.port)
    try:
        flag = exploit(conn)
        print('[+] flag:', flag.decode(errors='replace'))
    finally:
        conn.close()


if __name__ == '__main__':
    main()
