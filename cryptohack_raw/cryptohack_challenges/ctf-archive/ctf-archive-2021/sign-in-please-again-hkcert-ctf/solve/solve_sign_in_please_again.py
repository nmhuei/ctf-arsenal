#!/usr/bin/env python3
import ast
import base64
import hashlib
import os
import socket
import subprocess
import sys
import time

DEFAULT_CHALL = '/mnt/data/sipwork/sign-in-please-again-hkcert-ctf/files/chall_55080aab8f89e20affa8c6358b619a32.py'
ALPHABET = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

PROMPT_POW = '🔩 '.encode()
PROMPT_CMD = '🤖 '.encode()
PROMPT_PBOX = '😵 '.encode()
PROMPT_SALT = '🧂 '.encode()
PROMPT_HASH = '🔑 '.encode()
FLAG_MARK = '🏁'.encode()

# SHA-256 constants
K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]
MASK = 0xffffffff

def ror(x, n):
    return ((x >> n) | ((x << (32 - n)) & MASK)) & MASK

def sha256_compress(state, block: bytes):
    assert len(block) == 64
    w = [int.from_bytes(block[i:i+4], 'big') for i in range(0, 64, 4)]
    for i in range(16, 64):
        s0 = ror(w[i-15], 7) ^ ror(w[i-15], 18) ^ (w[i-15] >> 3)
        s1 = ror(w[i-2], 17) ^ ror(w[i-2], 19) ^ (w[i-2] >> 10)
        w.append((w[i-16] + s0 + w[i-7] + s1) & MASK)

    a, b, c, d, e, f, g, h = state
    for i in range(64):
        S1 = ror(e, 6) ^ ror(e, 11) ^ ror(e, 25)
        ch = (e & f) ^ ((~e) & g)
        temp1 = (h + S1 + ch + K[i] + w[i]) & MASK
        S0 = ror(a, 2) ^ ror(a, 13) ^ ror(a, 22)
        maj = (a & b) ^ (a & c) ^ (b & c)
        temp2 = (S0 + maj) & MASK
        h = g
        g = f
        f = e
        e = (d + temp1) & MASK
        d = c
        c = b
        b = a
        a = (temp1 + temp2) & MASK

    return [
        (state[0] + a) & MASK, (state[1] + b) & MASK,
        (state[2] + c) & MASK, (state[3] + d) & MASK,
        (state[4] + e) & MASK, (state[5] + f) & MASK,
        (state[6] + g) & MASK, (state[7] + h) & MASK,
    ]

def state_from_hex(hx: str):
    b = bytes.fromhex(hx)
    return [int.from_bytes(b[i:i+4], 'big') for i in range(0, 32, 4)]

def state_to_hex(state):
    return ''.join(f'{x:08x}' for x in state)

def md_from_state_hex(hx: str, block: bytes) -> str:
    return state_to_hex(sha256_compress(state_from_hex(hx), block))

def padding_block_tail(data_tail: bytes, total_msg_len: int) -> bytes:
    """Return the final 64-byte SHA-256 block when a previous full block exists.
    data_tail is the bytes after the previous 64-byte block(s). For this solve it
    is 1 byte (pepper recovery) or 2 bytes (password recovery).
    """
    assert 0 <= len(data_tail) <= 55
    return data_tail + b'\x80' + b'\x00' * (55 - len(data_tail)) + (total_msg_len * 8).to_bytes(8, 'big')

class Tube:
    def __init__(self, *, local=False, chall_path=None, host=None, port=None, timeout=20):
        self.local = local
        if local:
            chall_path = chall_path or os.environ.get('CHALL') or DEFAULT_CHALL
            env = os.environ.copy()
            env.setdefault('FLAG', 'hkcert21{LOCAL_TEST_FLAG}')
            # Run normally. Assertions must stay enabled for the real challenge path.
            self.p = subprocess.Popen(
                [sys.executable, '-u', chall_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
            )
            self.r = self.p.stdout
            self.w = self.p.stdin
        else:
            self.s = socket.create_connection((host, int(port)), timeout=timeout)
            self.s.settimeout(timeout)

    def close(self):
        try:
            if self.local:
                self.p.kill()
            else:
                self.s.close()
        except Exception:
            pass

    def recv(self, n=1):
        if self.local:
            b = self.r.read(n)
            if not b:
                raise EOFError('local process closed')
            return b
        b = self.s.recv(n)
        if not b:
            raise EOFError('remote connection closed')
        return b

    def send(self, data: bytes):
        if self.local:
            self.w.write(data)
            self.w.flush()
        else:
            self.s.sendall(data)

    def sendline(self, data):
        if isinstance(data, str):
            data = data.encode()
        self.send(data + b'\n')

    def recvuntil(self, marker: bytes) -> bytes:
        data = b''
        while not data.endswith(marker):
            data += self.recv(1)
        return data

    def recvline(self) -> bytes:
        data = b''
        while not data.endswith(b'\n'):
            data += self.recv(1)
        return data


def solve_pow(chal_b64: str) -> str:
    challenge = base64.b64decode(chal_b64)
    i = 0
    while True:
        response = i.to_bytes(8, 'little')
        if hashlib.sha256(challenge + response).digest().startswith(b'\x00\x00\x00'):
            return base64.b64encode(response).decode()
        i += 1


def pass_pow(t: Tube):
    line = t.recvline().decode().strip()  # 🔧 <challenge>
    challenge = line.split()[-1]
    answer = solve_pow(challenge)
    t.recvuntil(PROMPT_POW)
    t.sendline(answer)


def spy_hash(t: Tube, pbox, salt: bytes) -> str:
    t.recvuntil(PROMPT_CMD)
    t.sendline('🕵️')
    t.recvuntil(PROMPT_PBOX)
    t.sendline('[' + ','.join(map(str, pbox)) + ']')
    t.recvuntil(PROMPT_SALT)
    t.sendline(base64.b64encode(salt).decode())
    line = t.recvline().decode(errors='replace').strip()
    if not line.startswith('🔑 '):
        raise RuntimeError(f'spy failed: {line!r}')
    return line.split()[-1]


def login(t: Tube, password: bytes) -> str:
    t.recvuntil(PROMPT_CMD)
    t.sendline('🖥️')
    pbox_line = t.recvline().decode(errors='replace').strip()
    salt_line = t.recvline().decode(errors='replace').strip()
    pbox = ast.literal_eval(pbox_line.split(' ', 1)[1])
    salt = base64.b64decode(salt_line.split(' ', 1)[1])
    payload = password + salt + b'\x00'  # any pepper is accepted by auth()
    digest = hashlib.sha256(bytes(payload[i] for i in pbox)).hexdigest()
    t.recvuntil(PROMPT_HASH)
    t.sendline(digest)
    out = b''
    while True:
        try:
            out += t.recv(1)
            if FLAG_MARK in out and out.endswith(b'\n'):
                break
        except EOFError:
            break
    return out.decode(errors='replace')


def sigma_star_with_tail(*tail):
    # First 64 bytes: password || 00 00 00 00 || chosen_byte || 80 || 00...00 || a8
    # Then caller-controlled tail bytes, usually pepper or password_index, pepper.
    return list(range(16)) + [16] * 4 + [17, 18] + [16] * 41 + [19] + list(tail)


def recover_known_pepper_hash(t: Tube, verbose=True):
    # 16 identity calls: h = SHA256(password || 00 00 00 00 || r)
    identity = list(range(21))
    U = []
    for i in range(16):
        h = spy_hash(t, identity, b'\x00\x00\x00\x00')
        U.append(h)
        if verbose:
            print(f'[+] identity sample {i+1:02d}/16: {h}', flush=True)

    # 16 crafted calls. If an identity pepper r equals k, this crafted call has
    # the same first SHA-256 block as that identity hash. We can verify by
    # continuing h with all 256 possible second-block peppers.
    pbox = sigma_star_with_tail(20)  # length 65
    block_by_j = [padding_block_tail(bytes([j]), 65) for j in range(256)]
    expected = {}
    for h in U:
        for j, block in enumerate(block_by_j):
            expected[md_from_state_hex(h, block)] = (h, j)

    for k in range(16):
        v = spy_hash(t, pbox, bytes([0, k, 0x80, 0xA8]))
        if verbose:
            print(f'[+] pepper test k={k:02x}: {v}', flush=True)
        if v in expected:
            h, second_pepper = expected[v]
            if verbose:
                print(f'[+] recovered one first-call pepper: r=0x{k:02x}; second-call pepper was 0x{second_pepper:02x}')
                print(f'[+] reusable internal state h = {h}')
            return h, k
    return None, None


def recover_password(t: Tube, h_state_hex: str, known_first_pepper: int, verbose=True) -> bytes:
    password = bytearray()
    salt = bytes([0, known_first_pepper, 0x80, 0xA8])

    # Same h_state_hex and same total length for every character query, so build
    # one lookup table instead of doing 16 * 64 * 256 compressions.
    candidate = {}
    for c in ALPHABET:
        for pepper in range(256):
            block = padding_block_tail(bytes([c, pepper]), 66)
            candidate[md_from_state_hex(h_state_hex, block)] = c

    for idx in range(16):
        pbox = sigma_star_with_tail(idx, 20)  # length 66
        v = spy_hash(t, pbox, salt)
        if v not in candidate:
            raise RuntimeError(f'failed to recover password byte {idx}')
        found = candidate[v]
        password.append(found)
        if verbose:
            print(f'[+] pw[{idx:02d}] = {chr(found)!r}    current={password.decode()}', flush=True)
    return bytes(password)


def make_tube(argv_mode, chall_path=None, host=None, port=None):
    if argv_mode == 'local':
        return Tube(local=True, chall_path=chall_path)
    return Tube(local=False, host=host, port=port)


def solve_once(argv_mode, chall_path=None, host=None, port=None, verbose=True):
    t = make_tube(argv_mode, chall_path=chall_path, host=host, port=port)
    try:
        pass_pow(t)
        h, r = recover_known_pepper_hash(t, verbose=verbose)
        if h is None:
            if verbose:
                print('[-] no pepper hit this session; retrying with a new session')
            return None
        password = recover_password(t, h, r, verbose=verbose)
        print(f'[+] recovered password = {password!r}', flush=True)
        return login(t, password)
    finally:
        t.close()


def usage():
    print('Usage:')
    print('  python3 solve_sign_in_please_again_v2.py local [path/to/chall.py]')
    print('  python3 solve_sign_in_please_again_v2.py remote archive.cryptohack.org 60192')
    print('  python3 solve_sign_in_please_again_v2.py archive.cryptohack.org 60192')
    sys.exit(2)


def main():
    if len(sys.argv) < 2:
        usage()

    if sys.argv[1] == 'local':
        mode = 'local'
        chall_path = sys.argv[2] if len(sys.argv) >= 3 else None
        host = port = None
    elif sys.argv[1] == 'remote':
        if len(sys.argv) != 4:
            usage()
        mode = 'remote'
        chall_path = None
        host, port = sys.argv[2], sys.argv[3]
    elif len(sys.argv) == 3:
        mode = 'remote'
        chall_path = None
        host, port = sys.argv[1], sys.argv[2]
    else:
        usage()

    max_attempts = int(os.environ.get('MAX_ATTEMPTS', '8'))
    for attempt in range(1, max_attempts + 1):
        print(f'[*] attempt {attempt}/{max_attempts}', flush=True)
        try:
            out = solve_once(mode, chall_path=chall_path, host=host, port=port, verbose=True)
            if out is not None:
                print(out, end='')
                if '🏁' in out or 'hkcert' in out:
                    return
        except (EOFError, socket.timeout, ConnectionError, RuntimeError) as e:
            print(f'[-] attempt failed: {e}')
        time.sleep(0.2)
    raise SystemExit('[-] failed after all attempts; rerun to try more pepper samples')

if __name__ == '__main__':
    main()
