#!/usr/bin/env python3
import sys, re, os, socket, subprocess, time, math, random, select
from math import gcd

try:
    from fpylll import IntegerMatrix, LLL
except ImportError as e:
    raise SystemExit("Missing fpylll/cysignals. Install with: python3 -m pip install fpylll cysignals")

PREFIX = b'SECUREHASH_'
TARGET = b'pleasegivemetheflag'
TEXP = int.from_bytes(PREFIX + TARGET, 'big')


def H_exp(m: bytes) -> int:
    return int.from_bytes(PREFIX + m, 'big')


def recover_p_g(vals):
    # vals dict for b'a', b'b', b'c', b'd'. Same length => exponents are arithmetic progression step 1.
    ha,hb,hc,hd = vals[b'a'], vals[b'b'], vals[b'c'], vals[b'd']
    # h_a*h_c = h_b^2 mod p and h_b*h_d = h_c^2 mod p
    x1 = abs(ha*hc - hb*hb)
    x2 = abs(hb*hd - hc*hc)
    G = gcd(x1, x2)
    # The gcd is p with overwhelming probability, but it can be p times a tiny
    # accidental factor. Pick the prime factor that is larger than every output.
    from sympy import isprime, factorint
    maxh = max(vals.values())
    candidates = []
    if isprime(G):
        candidates.append(G)
    fac = factorint(G, limit=1_000_000)
    for q, e in fac.items():
        q = int(q)
        if q > maxh and q.bit_length() <= 256 and isprime(q):
            candidates.append(q)
    # If factorint left a composite cofactor, repeatedly divide known small
    # factors from G and test the remaining cofactor too.
    rem = G
    for q, e in fac.items():
        for _ in range(e):
            if rem % int(q) == 0:
                rem //= int(q)
    if rem > maxh and rem.bit_length() <= 256 and isprime(rem):
        candidates.append(int(rem))
    candidates = sorted(set(candidates), key=lambda x: x.bit_length(), reverse=True)
    if not candidates:
        raise ValueError(f"could not isolate p from gcd bits={G.bit_length()} factors={fac}")
    p = candidates[0]
    if p <= 2 or p.bit_length() > 256 or p.bit_length() < 128:
        raise ValueError(f"bad recovered p: bits={p.bit_length()} p={p}")
    # For adjacent exponents: h_b = h_a * g mod p.
    g = (hb * pow(ha, -1, p)) % p
    return p, g


def hash_with(m: bytes, p: int, g: int) -> int:
    return pow(g, H_exp(m), p)


def find_collision_mod(n: int, max_len=160, verbose=True) -> bytes:
    """Find lowercase m such that int(PREFIX+m) == int(PREFIX+TARGET) mod n.
    Uses a lattice embedding over digits y_i in [0,25], where m_i = ord('a') + y_i.
    """
    # More length means more valid strings. L=70 is usually enough, but keep fallbacks.
    attempts = []
    for L in [70, 76, 84, 96, 112, 128, 160]:
        for K in [1000, 100, 10000, 10, 1, 1000000]:
            attempts.append((L,K))
    center = 13
    pref_int = int.from_bytes(PREFIX, 'big')
    for L, K in attempts:
        weights = [pow(256, L-1-i, n) for i in range(L)]
        sumw = sum(weights) % n
        base = (pref_int * pow(256, L, n) + 97 * sumw) % n
        C = (TEXP - base) % n
        Cp = (C - center * sumw) % n

        A = IntegerMatrix(L+2, L+2)
        for i, w in enumerate(weights):
            A[i, i] = 1
            A[i, L] = K * w
        A[L, L] = K * n
        A[L+1, L] = K * Cp
        A[L+1, L+1] = 1

        if verbose:
            print(f"[*] LLL try L={L}, K={K}", flush=True)
        t0 = time.time()
        LLL.reduction(A, delta=0.99)
        if verbose:
            print(f"    LLL done in {time.time()-t0:.2f}s", flush=True)

        for r in range(A.nrows):
            v = [int(A[r, c]) for c in range(A.ncols)]
            if abs(v[-1]) != 1 or v[L] != 0:
                continue
            # If last coord is +1, the vector represents z*w == -Cp; negate z.
            z = v[:L]
            if v[-1] == 1:
                z = [-x for x in z]
            y = [x + center for x in z]
            if all(0 <= yy <= 25 for yy in y):
                if (sum((y[i] * weights[i]) % n for i in range(L)) - C) % n == 0:
                    m = bytes([97 + yy for yy in y])
                    if m != TARGET:
                        if verbose:
                            print(f"[+] collision length={L}: {m.decode()}", flush=True)
                        return m
        if verbose:
            print("    no bounded row found", flush=True)
    raise RuntimeError("failed to find lowercase modular collision; retry with larger lengths")


class LocalProc:
    def __init__(self, argv, env=None):
        self.p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    def ask(self, s: str) -> str:
        self.p.stdin.write((s + "\n").encode())
        self.p.stdin.flush()
        return self.p.stdout.readline().decode(errors='replace').strip()
    def readline_timeout(self, timeout=2):
        r,_,_ = select.select([self.p.stdout], [], [], timeout)
        if not r:
            return None
        data = self.p.stdout.readline()
        if not data:
            return None
        return data.decode(errors='replace').strip()
    def close(self):
        try: self.p.kill()
        except Exception: pass

class RemoteSock:
    def __init__(self, host, port):
        self.s = socket.create_connection((host, int(port)), timeout=20)
        self.buf = b''
    def _readline(self):
        while b'\n' not in self.buf:
            chunk = self.s.recv(4096)
            if not chunk:
                raise EOFError('remote closed')
            self.buf += chunk
        line, self.buf = self.buf.split(b'\n',1)
        return line.decode(errors='replace').strip()
    def ask(self, s: str) -> str:
        self.s.sendall((s+'\n').encode())
        return self._readline()
    def readline_timeout(self, timeout=2):
        old = self.s.gettimeout()
        self.s.settimeout(timeout)
        try:
            return self._readline()
        except Exception:
            return None
        finally:
            self.s.settimeout(old)
    def close(self):
        self.s.close()


def parse_hash_line(line: str) -> int:
    m = re.search(r'=\s*([0-9a-fA-F]{64})', line)
    if not m:
        raise ValueError(f"could not parse hash line: {line!r}")
    return int(m.group(1), 16)


def run(io, verify=True):
    vals = {}
    for msg in ['a','b','c','d']:
        line = io.ask(msg)
        print(f"[<] {line}", flush=True)
        vals[msg.encode()] = parse_hash_line(line)
    p, g = recover_p_g(vals)
    print(f"[+] recovered p bits={p.bit_length()} p={p}", flush=True)
    print(f"[+] recovered g={g}", flush=True)
    if verify:
        for m,h in vals.items():
            assert hash_with(m, p, g) == h, (m, 'bad p/g')
        print("[+] local model verifies the 4 oracle hashes", flush=True)
    coll = find_collision_mod(p-1, verbose=True)
    ht = hash_with(TARGET, p, g)
    hc = hash_with(coll, p, g)
    print(f"[+] h(collision) == h(target): {hc == ht}", flush=True)
    line = io.ask(coll.decode())
    print(f"[<] {line}", flush=True)
    extra = io.readline_timeout(3) if hasattr(io, 'readline_timeout') else None
    if extra:
        print(f"[<] {extra}", flush=True)
        line += "\n" + extra
    return line, coll


def main():
    if len(sys.argv) == 1 or sys.argv[1] == 'local':
        chall = sys.argv[2] if len(sys.argv) > 2 else '/mnt/data/c0ll1d3r_work/c0ll1d3r-firebird-internal-ctf/files/chall_5a135d0a164200ace923e795da7fa350.py'
        env = os.environ.copy(); env['FLAG'] = 'firebird{LOCAL_TEST_FLAG}'
        io = LocalProc([sys.executable, chall], env=env)
    elif sys.argv[1] == 'remote':
        host = sys.argv[2] if len(sys.argv) > 2 else 'archive.cryptohack.org'
        port = int(sys.argv[3] if len(sys.argv) > 3 else 9391)
        io = RemoteSock(host, port)
    else:
        # shorthand: solve.py host port
        io = RemoteSock(sys.argv[1], int(sys.argv[2]))
    try:
        run(io)
    finally:
        io.close()

if __name__ == '__main__':
    main()
