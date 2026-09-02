#!/usr/bin/env python3
import os, sys, socket, subprocess, time, hashlib, math, random, select
from math import log
import numpy as np
from numba import njit

# fpylll was installed into this path in the working sandbox
if os.path.isdir('/mnt/data/pip_fpylll'):
    sys.path.insert(0, '/mnt/data/pip_fpylll')
from fpylll import IntegerMatrix, LLL, CVP

HOST = os.environ.get('HOST', 'archive.cryptohack.org')
PORT = int(os.environ.get('PORT', '35802'))

# Try to locate chal.py both in this sandbox layout and in a normal extracted repo.
def find_chal():
    candidates = [
        os.environ.get('CHAL', ''),
        os.path.join(os.path.dirname(__file__), 'chal.py'),
        os.path.join(os.path.dirname(__file__), '..', 'chal.py'),
        os.path.join(os.path.dirname(__file__), '..', 'files', 'chal_ab50c49bda5728e0370b640b328c4eb4.py'),
        '/mnt/data/darkarts/dark-arts-codegate-ctf/files/chal_ab50c49bda5728e0370b640b328c4eb4.py',
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return os.path.abspath(c)
    raise FileNotFoundError('Could not find chal.py. Set CHAL=/path/to/chal.py')

CHAL = find_chal()

# ---------- I/O ----------
class Tube:
    def __init__(self, mode):
        self.mode = mode
        self.buf = bytearray()
        if mode == 'local':
            env = os.environ.copy(); env['FLAG'] = 'LOCAL_FLAG_OK'
            self.p = subprocess.Popen([sys.executable, '-u', CHAL], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        else:
            self.s = socket.create_connection((HOST, PORT), timeout=60)
            self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    def send(self, data: bytes):
        if self.mode == 'local':
            if self.p.poll() is not None:
                raise EOFError('local process already exited before send')
            try:
                self.p.stdin.write(data); self.p.stdin.flush()
            except BrokenPipeError as e:
                raise EOFError('broken pipe to local process') from e
        else:
            self.s.sendall(data)
    def _recv_some(self):
        if self.mode == 'local':
            fd = self.p.stdout.fileno()
            rr, _, _ = select.select([fd], [], [], 10)
            if not rr:
                if self.p.poll() is not None:
                    b = b''
                else:
                    raise TimeoutError('no local output for 10s')
            else:
                b = os.read(fd, 65536)
        else:
            b = self.s.recv(65536)
        if not b:
            if self.mode == 'local':
                try: err = self.p.stderr.read().decode(errors='replace')
                except Exception: err = ''
                raise EOFError('EOF from local process. stderr:\n' + err)
            raise EOFError('EOF from remote')
        self.buf.extend(b)
    def read_lines(self, n):
        while self.buf.count(10) < n:
            self._recv_some()
        out = []
        start = 0
        for _ in range(n):
            idx = self.buf.index(10, start)
            out.append(bytes(self.buf[start:idx]).decode().strip())
            start = idx + 1
        del self.buf[:start]
        return out
    def line(self) -> str:
        return self.read_lines(1)[0]
    def close(self):
        try:
            if self.mode == 'local': self.p.kill()
            else: self.s.close()
        except Exception:
            pass

def query_many(tube, xs, chunk=None):
    # Larger batches are critical on the remote: the server has a 300s alarm,
    # and small chunks make stage 2 spend most of its time on network RTTs.
    xs = list(xs)
    out = []
    if chunk is None:
        chunk = int(os.environ.get('QUERY_CHUNK', '5000'))
    for off in range(0, len(xs), chunk):
        part = xs[off:off+chunk]
        data = ''.join(f'0\n{x}\n' for x in part).encode()
        tube.send(data)
        out.extend(int(x) for x in tube.read_lines(len(part)))
    return out

def guess_mode(tube, mode):
    tube.send(f'1\n{mode}\n'.encode())

def submit_key(tube, key):
    tube.send(('1\n' + '\n'.join(str(int(x)) for x in key) + '\n').encode())

# ---------- hash vectors ----------
def g2_hash_bits(x):
    n = int.from_bytes(hashlib.sha256(str(x).encode()).digest(), 'big')
    return [(n >> i) & 1 for i in range(256)]

def g3_vec(x):
    n = int.from_bytes(hashlib.sha256(str(x).encode()).digest(), 'big')
    out = []
    for _ in range(64):
        out.append(n % 5); n //= 5
    return out

def g4_vec(x):
    h = hashlib.sha256(str(x).encode()).digest()
    out = []
    for _ in range(16):
        out.append(int.from_bytes(h, 'big'))
        h = hashlib.sha256(h).digest()
    return out

# ---------- stage 2 likelihood ----------
def precompute_stage2():
    Ps = []
    for m in range(257):
        dist = [0]*35; dist[0] = 1
        for _ in range(m):
            nd = [0]*35
            for r, v in enumerate(dist):
                nd[r] += v; nd[(r+1) % 35] += v
            dist = nd
        tot = sum(dist); out = [0.0]*5
        for r, v in enumerate(dist):
            out[((r % 5) + (r % 7)) % 5] += v / tot
        Ps.append(out)
    return Ps

STAGE2_PS = precompute_stage2()
STAGE2_LOG_PRIOR = [math.log(math.comb(256, m)) - 256*math.log(2) for m in range(257)]

def _logsumexp(vals):
    mx = max(vals)
    return mx + math.log(sum(math.exp(v-mx) for v in vals))

def stage2_score(counts):
    vals = []
    for m, P in enumerate(STAGE2_PS):
        if any(counts[i] and P[i] == 0 for i in range(5)):
            continue
        vals.append(STAGE2_LOG_PRIOR[m] + sum(counts[i] * log(P[i]) for i in range(5)))
    return _logsumexp(vals) - sum(counts) * log(0.2)

# ---------- GF(5) algebra for stage 3 ----------
INV5 = np.array([0,1,3,2,4], dtype=np.uint8)

@njit
def gauss5(M):
    R, Cp1 = M.shape
    C = Cp1 - 1
    inv = np.array([0,1,3,2,4], dtype=np.uint8)
    sub = np.empty((5,5,5), dtype=np.uint8)
    for f in range(5):
        for x in range(5):
            for y in range(5):
                sub[f,x,y] = (x - f*y) % 5
    piv_cols = np.empty(min(R,C), dtype=np.int64)
    r = 0
    for c in range(C):
        p = -1
        for i in range(r, R):
            if M[i,c] != 0:
                p = i; break
        if p == -1:
            continue
        if p != r:
            for j in range(c, Cp1):
                tmp = M[r,j]; M[r,j] = M[p,j]; M[p,j] = tmp
        invp = inv[M[r,c]]
        if invp != 1:
            for j in range(c, Cp1):
                M[r,j] = (M[r,j] * invp) % 5
        for i in range(r+1, R):
            f = M[i,c]
            if f != 0:
                for j in range(c, Cp1):
                    M[i,j] = sub[f, M[i,j], M[r,j]]
        piv_cols[r] = c
        r += 1
        if r == R:
            break
    sol = np.zeros(C, dtype=np.uint8)
    for rr in range(r-1, -1, -1):
        c = piv_cols[rr]
        val = M[rr, C]
        for j in range(c+1, C):
            if M[rr,j] != 0 and sol[j] != 0:
                val = (val - M[rr,j] * sol[j]) % 5
        sol[c] = val
    return sol, r

def inv_matrix_np(A):
    A = np.array(A, dtype=np.uint8)
    n = A.shape[0]
    M = np.concatenate([A % 5, np.eye(n, dtype=np.uint8)], axis=1).astype(np.uint8)
    r = 0
    for c in range(n):
        pivs = np.nonzero(M[r:,c] % 5)[0]
        if len(pivs) == 0:
            continue
        p = r + int(pivs[0])
        if p != r: M[[r,p]] = M[[p,r]]
        inv = int(INV5[M[r,c]])
        M[r] = (M[r].astype(np.uint16) * inv % 5).astype(np.uint8)
        mask = np.nonzero(M[:,c])[0]
        mask = mask[mask != r]
        if len(mask):
            fac = M[mask,c].astype(np.int16)
            M[mask] = ((M[mask].astype(np.int16) - fac[:,None] * M[r].astype(np.int16)) % 5).astype(np.uint8)
        r += 1
        if r == n: break
    if r < n:
        return None
    return M[:,n:]

# precompute quadratic monomial pair positions
PAIR_I = []
PAIR_J = []
for _i in range(64):
    for _j in range(_i+1,64):
        PAIR_I.append(_i); PAIR_J.append(_j)
PAIR_I = np.array(PAIR_I); PAIR_J = np.array(PAIR_J)
NMON = 64 + len(PAIR_I)

def select_y1_basis(Hs, ys):
    ones = [i for i, y in enumerate(ys) if y == 1]
    # Try consecutive windows first; this is normally enough.
    for off in range(max(1, len(ones)-63)):
        cand = ones[off:off+64]
        if len(cand) < 64: break
        inv = inv_matrix_np([Hs[i] for i in cand])
        if inv is not None:
            return cand, inv
    # Fallback: random windows.
    for _ in range(500):
        cand = random.sample(ones, 64)
        inv = inv_matrix_np([Hs[i] for i in cand])
        if inv is not None:
            return cand, inv
    raise RuntimeError('could not find y=1 invertible basis')

def solve_stage3_key(Hs, ys):
    sel, InvM = select_y1_basis(Hs, ys)
    base = set(sel)
    rows, rhs = [], []
    for i, h in enumerate(Hs):
        if i in base or ys[i] != 1:
            continue
        coeff = (np.array(h, dtype=np.uint16) @ InvM.astype(np.uint16) % 5).astype(np.uint8)
        c0 = int(coeff.sum() % 5)
        a = (2 * coeff.astype(np.uint16) % 5).astype(np.uint8)
        lin = ((2*c0*a.astype(np.uint16) + a.astype(np.uint16)*a.astype(np.uint16) + a.astype(np.uint16)) % 5).astype(np.uint8)
        quad = (2 * a[PAIR_I].astype(np.uint16) * a[PAIR_J].astype(np.uint16) % 5).astype(np.uint8)
        rows.append(np.concatenate([lin, quad]))
        rhs.append((-(c0*c0 + c0 + 3)) % 5)   # (L-1)(L-3)=L^2+L+3
        if len(rows) >= NMON + 32:
            break
    if len(rows) < NMON:
        raise RuntimeError(f'not enough y=1 equations: {len(rows)}')
    A = np.vstack(rows).astype(np.uint8)
    b = np.array(rhs, dtype=np.uint8)
    M = np.concatenate([A, b.reshape(-1,1)], axis=1).astype(np.uint8)
    sol, rank = gauss5(M)
    if rank < NMON:
        raise RuntimeError(f'quadratic system rank too small: {rank}')
    bits = [int(x) for x in sol[:64]]
    if not all(x in (0,1) for x in bits):
        raise RuntimeError('linearized solution did not recover Boolean variables')
    rvec = np.array([(1 + 2*x) % 5 for x in bits], dtype=np.uint8)
    key = (InvM.astype(np.uint16) @ rvec.astype(np.uint16) % 5).astype(int).tolist()
    if not all(0 <= x <= 3 for x in key):
        raise RuntimeError('recovered stage3 key outside 0..3')
    return key

# ---------- stage 4 lattice ----------
def inv_mat_mod(A, p):
    n = len(A)
    M = [row[:] + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(A)]
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, n):
            v = M[i][c] % p
            if v and math.gcd(v, p) == 1:
                piv = i; break
        if piv is None:
            raise ValueError('singular/non-unit pivot')
        M[r], M[piv] = M[piv], M[r]
        inv = pow(M[r][c] % p, -1, p)
        M[r] = [(v * inv) % p for v in M[r]]
        for i in range(n):
            if i != r and M[i][c] % p:
                fac = M[i][c] % p
                M[i] = [(M[i][j] - fac * M[r][j]) % p for j in range(2*n)]
        r += 1
    return [row[n:] for row in M]

def mat_vec_mod(row, M, p):
    return [sum(row[i] * M[i][j] for i in range(len(row))) % p for j in range(len(M[0]))]

def verify_g4_key(key, Hs, ys, p, q):
    for h, y in zip(Hs, ys):
        prod = sum(ki * hi for ki, hi in zip(key, h))
        if (prod % p + prod % q) % p != y:
            return False
    return True

def solve_stage4_key(Hs, ys, p, q):
    total = len(Hs)
    idxs = list(range(total))
    for m in [36, 40, 44, 48, 56, 64]:
        if m > total: continue
        for attempt in range(500):
            # random basis among available samples; then deterministic remainder
            cand = random.sample(idxs[:min(total, 100)], 16)
            try:
                Inv = inv_mat_mod([Hs[i] for i in cand], p)
            except Exception:
                continue
            rem = [i for i in idxs if i not in set(cand)][:m-16]
            coeffs = [mat_vec_mod(Hs[i], Inv, p) for i in rem]
            B = IntegerMatrix(m, m)
            for i in range(16):
                B[i, i] = 1
                for j, c in enumerate(coeffs):
                    B[i, 16+j] = int(c[i])
            for j in range(m-16):
                B[16+j, 16+j] = int(p)
            try:
                LLL.reduction(B)
                target = tuple(int(ys[i]) for i in cand + rem)
                cv = CVP.closest_vector(B, target)
            except Exception:
                continue
            u = [int(cv[i]) % p for i in range(16)]
            key = [sum(Inv[i][j] * u[j] for j in range(16)) % p for i in range(16)]
            if verify_g4_key(key, Hs, ys, p, q):
                return key
    raise RuntimeError('stage4 lattice recovery failed')

# ---------- solve all stages ----------
def solve(tube):
    START_TIME=time.time()
    line = tube.line(); print('[*]', line, flush=True)
    assert 'Challenge 1' in line
    for r in range(64):
        xs = [1 << i for i in range(20)]
        outs = query_many(tube, xs)
        guess_mode(tube, 1 if any(outs) else 0)
    line = tube.line(); print('[*]', line, flush=True)
    assert 'Challenge 2' in line

    # Fixed-sample likelihood test for stage 2; with chunked I/O this is fast
    # and much safer than an aggressive early-stop test.
    for r in range(64):
        N = int(os.environ.get('STAGE2_N', '4000'))
        outs = query_many(tube, range(N), chunk=N)
        counts = [0]*5
        for o in outs:
            counts[o] += 1
        sc = stage2_score(counts)
        decision = 0 if sc >= 0.0 else 1
        guess_mode(tube, decision)
        print(f'[*] stage2 round {r+1}/64 score={sc:.2f} mode={decision} elapsed={time.time()-START_TIME:.1f}s', flush=True)
    line = tube.line(); print('[*]', line, flush=True)
    assert 'Challenge 3' in line

    N3 = int(os.environ.get('STAGE3_N', '6500'))
    ys3 = query_many(tube, range(N3), chunk=5000)
    Hs3 = [g3_vec(i) for i in range(N3)]
    t0 = time.time()
    key3 = solve_stage3_key(Hs3, ys3)
    print(f'[*] stage3 key recovered in {time.time()-t0:.2f}s', flush=True)
    submit_key(tube, key3)

    line = tube.line(); print('[*]', line, flush=True)
    assert 'Challenge 4' in line
    p = int(tube.line()); q = int(tube.line())
    print('[*] got p,q', flush=True)
    N4 = int(os.environ.get('STAGE4_N', '120'))
    ys4 = query_many(tube, range(N4), chunk=N4)
    Hs4 = [g4_vec(i) for i in range(N4)]
    t0 = time.time()
    key4 = solve_stage4_key(Hs4, ys4, p, q)
    print(f'[*] stage4 key recovered in {time.time()-t0:.2f}s', flush=True)
    submit_key(tube, key4)
    flag = tube.line()
    return flag

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'local'
    t = Tube(mode)
    try:
        flag = solve(t)
        print(flag)
    finally:
        t.close()
