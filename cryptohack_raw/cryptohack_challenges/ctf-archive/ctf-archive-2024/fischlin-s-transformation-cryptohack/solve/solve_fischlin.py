#!/usr/bin/env python3
import glob
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
from hashlib import sha512
from pathlib import Path

p = 0x1ed344181da88cae8dc37a08feae447ba3da7f788d271953299e5f093df7aaca987c9f653ed7e43bad576cc5d22290f61f32680736be4144642f8bea6f5bf55ef
q = 0xf69a20c0ed4465746e1bd047f57223dd1ed3fbc46938ca994cf2f849efbd5654c3e4fb29f6bf21dd6abb662e911487b0f9934039b5f20a23217c5f537adfaaf7
g = 2
THRESH = 2 ** (512 - 6)


def ro(a0, a1, e, e0, e1, z0, z1):
    h = sha512(b'my')
    h.update(str(a0).encode()); h.update(b'very')
    h.update(str(a1).encode()); h.update(b'cool')
    h.update(str(e).encode());  h.update(b'random')
    h.update(str(e0).encode()); h.update(b'oracle')
    h.update(str(e1).encode()); h.update(b'for')
    h.update(str(z0).encode()); h.update(b'fischlin')
    h.update(str(z1).encode())
    return int.from_bytes(h.digest(), 'big')


def w0_could_be_real(proof, w0):
    a0, a1 = proof['a0'], proof['a1']
    E, e0, e1 = proof['e'], proof['e0'], proof['e1']
    z0, z1 = proof['z0'], proof['z1']

    if (e0 ^ e1) != E:
        return False

    # If branch 0 was real, r0 is fixed during the whole Fischlin search.
    r0 = (z0 - e0 * w0) % q
    if pow(g, r0, p) != a0 % p:
        return False

    # Recreate every previous RO query that would have been made for branch 0 real.
    # Any earlier accepting query contradicts the published stopping counter E.
    for Ep in range(E):
        e0p = Ep ^ e1       # branch 1 is simulated/fixed under this hypothesis
        z0p = (r0 + e0p * w0) % q
        if ro(a0, a1, Ep, e0p, e1, z0p, z1) < THRESH:
            return False
    return True


class Tube:
    def __init__(self, argv=None, cwd=None, host=None, port=None):
        self.buf = b''
        if host is not None:
            self.sock = socket.create_connection((host, int(port)), timeout=10)
            self.sock.settimeout(10)
            self.proc = None
        else:
            env = os.environ.copy()
            env.setdefault('FLAG', 'crypto{LOCAL_TEST_FLAG}')
            self.proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)
            self.sock = None

    def _recv1(self):
        b = self.sock.recv(1) if self.sock else self.proc.stdout.read(1)
        if not b:
            raise EOFError(self.buf.decode(errors='replace'))
        self.buf += b

    def read_until(self, marker):
        if isinstance(marker, str):
            marker = marker.encode()
        while marker not in self.buf:
            self._recv1()
        i = self.buf.index(marker) + len(marker)
        out, self.buf = self.buf[:i], self.buf[i:]
        return out.decode(errors='replace')

    def read_line(self):
        return self.read_until(b'\n')

    def sendline(self, s):
        data = str(s).encode() + b'\n'
        if self.sock:
            self.sock.sendall(data)
        else:
            self.proc.stdin.write(data)
            self.proc.stdin.flush()

    def drain(self):
        if self.sock:
            self.sock.settimeout(1)
            chunks = [self.buf]
            self.buf = b''
            try:
                while True:
                    x = self.sock.recv(4096)
                    if not x:
                        break
                    chunks.append(x)
            except Exception:
                pass
            return b''.join(chunks).decode(errors='replace')
        try:
            rest = self.proc.communicate(timeout=2)[0]
        except subprocess.TimeoutExpired:
            rest = b''
        out = self.buf + (rest or b'')
        self.buf = b''
        return out.decode(errors='replace')


def parse_int(prefix, text):
    m = re.search(re.escape(prefix) + r'\s*=\s*(\d+)', text)
    if not m:
        raise ValueError(f'Cannot parse {prefix} from: {text!r}')
    return int(m.group(1))


def solve(io):
    for rnd in range(64):
        for attempt in range(16):
            io.read_until('y0 = '); int(io.read_line().strip())
            io.read_until('y1 = '); int(io.read_line().strip())

            io.read_until('which witness do you want to see?')
            io.sendline(0)          # always leak w0
            w0 = parse_int('w0', io.read_line())

            io.read_until('here is your fishlin transcript')
            line = io.read_line().strip()
            if not line:
                line = io.read_line().strip()
            proof = json.loads(line)

            possible0 = w0_could_be_real(proof, w0)
            last_try = (attempt == 15)
            if (not possible0) or last_try:
                guess = 1 if not possible0 else 0
                io.read_until('do you think you can guess my witness? (y,n)')
                io.sendline('y')
                io.read_until('which witness did the prover use?')
                io.sendline(guess)
                print(f'round {rnd:02d}: attempt {attempt+1:02d}, e={proof["e"]}, possible0={possible0}, guess={guess}', flush=True)
                break

            io.read_until('do you think you can guess my witness? (y,n)')
            io.sendline('n')

        result = io.read_until('\n')
        sys.stdout.write(result)
        if "didn't guess" in result:
            print(io.drain())
            return False

    print(io.drain())
    return True


def make_local_tube():
    root = Path.cwd()
    chal_matches = list(root.rglob('chal_*.py')) + list(root.rglob('chal.py'))
    params_matches = list(root.rglob('params_*.py')) + list(root.rglob('params.py'))
    if not chal_matches or not params_matches:
        raise SystemExit('Run from the extracted challenge directory, or use: python3 solve_fischlin.py HOST PORT')

    tmp = Path(tempfile.mkdtemp(prefix='fischlin_local_'))
    shutil.copy(chal_matches[0], tmp / 'chal.py')
    shutil.copy(params_matches[0], tmp / 'params.py')

    # Let the challenge run even when pycryptodome is not installed.
    util = tmp / 'Crypto' / 'Util'
    util.mkdir(parents=True)
    (tmp / 'Crypto' / '__init__.py').write_text('')
    (util / '__init__.py').write_text('')
    (util / 'number.py').write_text('def bytes_to_long(b):\n    return int.from_bytes(b, "big")\n')

    return Tube(argv=[sys.executable, 'chal.py'], cwd=str(tmp))


if __name__ == '__main__':
    if len(sys.argv) == 3:
        tube = Tube(host=sys.argv[1], port=int(sys.argv[2]))
    else:
        tube = make_local_tube()
    raise SystemExit(0 if solve(tube) else 1)
