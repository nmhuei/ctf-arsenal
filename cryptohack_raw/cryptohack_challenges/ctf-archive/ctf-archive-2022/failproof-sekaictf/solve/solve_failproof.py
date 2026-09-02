#!/usr/bin/env python3
import ast, hashlib, os, socket, subprocess, sys, time
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'failproof-sekaictf' / 'files' / 'source_208d9c71e130149c2d9c6edf27242d25.py'
SEGMENT_LEN = 32
NVAR = SEGMENT_LEN * 8
ROWS_PER_CONN = 128
PRIME = 1000003

def gen_pubkey(secret: bytes, hasher=hashlib.sha256) -> list[int]:
    def h(m): return hasher(m).digest()
    state = h(secret)
    pubkey = []
    for _ in range(len(h(b'0')) * 4):
        pubkey.append(int.from_bytes(state, 'big'))
        state = h(state)
    return pubkey

def row_bits(mask: int) -> list[int]:
    # int.from_bytes(block,'big') => bit 255 is first byte MSB, bit 0 is last byte LSB.
    return [(mask >> (NVAR - 1 - j)) & 1 for j in range(NVAR)]

def parse_output(data: str):
    lines = [ln.strip() for ln in data.splitlines() if ln.strip()]
    # Sometimes banners/noise could exist; find secret hex and list line.
    secret = None
    enc = None
    for ln in lines:
        if len(ln) == 32 and all(c in '0123456789abcdefABCDEF' for c in ln):
            secret = bytes.fromhex(ln)
        elif ln.startswith('['):
            try:
                x = ast.literal_eval(ln)
                if isinstance(x, list) and x and isinstance(x[0], list):
                    enc = x
            except Exception:
                pass
    if secret is None or enc is None:
        raise ValueError(f'Could not parse output:\n{data!r}')
    return secret, enc

def collect_local(flag: bytes, n=3):
    samples = []
    env = os.environ.copy(); env['FLAG'] = flag.decode('latin1')
    for _ in range(n):
        out = subprocess.check_output([sys.executable, str(SRC)], env=env, text=True)
        samples.append(parse_output(out))
    return samples

def recv_all(host, port, timeout=8.0):
    with socket.create_connection((host, int(port)), timeout=timeout) as s:
        s.settimeout(timeout)
        chunks = []
        while True:
            try:
                data = s.recv(65536)
            except socket.timeout:
                break
            if not data:
                break
            chunks.append(data)
        return b''.join(chunks).decode('utf-8', 'replace')

def collect_remote(host, port, n=3):
    samples = []
    for i in range(n):
        data = recv_all(host, port)
        secret, enc = parse_output(data)
        samples.append((secret, enc))
        print(f'[+] collected {i+1}/{n}: blocks={len(enc)}', file=sys.stderr)
    return samples

def gauss_mod(A, b, p=PRIME):
    # Solve A x = b mod p. A can be overdetermined. Returns one unique solution
    # if rank reaches number of variables.
    m = len(A)
    n = len(A[0])
    aug = [ [(v % p) for v in A[i]] + [b[i] % p] for i in range(m) ]
    pivots = []
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, m):
            if aug[i][c] % p:
                piv = i; break
        if piv is None:
            continue
        aug[r], aug[piv] = aug[piv], aug[r]
        inv = pow(aug[r][c], -1, p)
        rowr = aug[r]
        for j in range(c, n+1):
            rowr[j] = (rowr[j] * inv) % p
        # eliminate all rows for direct RREF; dimensions small enough.
        for i in range(m):
            if i == r: continue
            factor = aug[i][c] % p
            if factor:
                rowi = aug[i]
                for j in range(c, n+1):
                    rowi[j] = (rowi[j] - factor * rowr[j]) % p
        pivots.append(c)
        r += 1
        if r == n:
            break
    if r < n:
        raise ValueError(f'matrix rank only {r}/{n}; collect more samples')
    x = [0] * n
    for row_idx, c in enumerate(pivots[:n]):
        x[c] = aug[row_idx][n] % p
    return x

def solve_samples(samples):
    if not samples:
        raise ValueError('no samples')
    nblocks = len(samples[0][1])
    rows = []
    ys_by_block = [[] for _ in range(nblocks)]
    for secret, enc in samples:
        if len(enc) != nblocks:
            raise ValueError('inconsistent number of encrypted blocks')
        pub = gen_pubkey(secret)
        for i, mask in enumerate(pub):
            rows.append(row_bits(mask))
            for bi in range(nblocks):
                ys_by_block[bi].append(enc[bi][i])
    out = b''
    for bi, y in enumerate(ys_by_block):
        x = gauss_mod(rows, y)
        bad = [v for v in x if v not in (0, 1)]
        if bad:
            raise ValueError(f'block {bi}: non-bit solution values {bad[:10]}')
        val = 0
        for bit in x:
            val = (val << 1) | bit
        block = val.to_bytes(SEGMENT_LEN, 'big')
        out += block
        print(f'[+] block {bi}: {block!r}', file=sys.stderr)
    return out.rstrip(b'\x00')

def main():
    if len(sys.argv) >= 2 and sys.argv[1] == 'local':
        flag = sys.argv[2].encode() if len(sys.argv) > 2 else b'SEKAI{local_test_flag_for_failproof_solver_12345}'
        samples = collect_local(flag, n=int(sys.argv[3]) if len(sys.argv)>3 else 3)
        rec = solve_samples(samples)
        print(rec.decode('latin1'))
    elif len(sys.argv) >= 4 and sys.argv[1] == 'remote':
        host, port = sys.argv[2], int(sys.argv[3])
        n = int(sys.argv[4]) if len(sys.argv) > 4 else 3
        samples = collect_remote(host, port, n=n)
        rec = solve_samples(samples)
        print(rec.decode('latin1'))
    else:
        print(f'Usage:\n  {sys.argv[0]} local [flag] [samples]\n  {sys.argv[0]} remote HOST PORT [samples]', file=sys.stderr)
        raise SystemExit(2)

if __name__ == '__main__':
    main()
