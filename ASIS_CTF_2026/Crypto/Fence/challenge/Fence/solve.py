import json, time, hashlib, hmac
import multiprocessing as mp
import fpylll
from fpylll import IntegerMatrix, LLL, BKZ

with open('flag.enc') as f:
    data = json.load(f)

N = data['N']
Q = data['Q']
W = data['W']
R = data['R']
HS = data['H']
CS = data['C']
d = b'\x3a\x91\xf0\x7d\x14\x68\xbc\x29'

def sh(a, k):
    k %= 2 * N
    s = -1 if k >= N else 1
    if k >= N:
        k -= N
    b = [0] * N
    for i in range(N):
        if i + k < N:
            b[i + k] = s * a[i]
        else:
            b[i + k - N] = -s * a[i]
    return b

def ky(a, b, s):
    u = min(tuple(sh(a, i) + sh(b, i)) for i in range(2 * N))
    return hashlib.sha3_256(d + s + bytes(i + 1 for i in u)).digest()

def dc(a, b, h, z):
    s, c, t = bytes.fromhex(z['S']), bytes.fromhex(z['C']), bytes.fromhex(z['T'])
    k = ky(a, b, s)
    u = json.dumps({'N': N, 'Q': Q, 'H': h}, sort_keys=True, separators=(',', ':')).encode()
    if not hmac.compare_digest(t, hmac.new(k, d + u + s + c, hashlib.sha256).digest()[:16]):
        raise ValueError('HMAC mismatch!')
    z_stream = hashlib.shake_256(d + k + s).digest(len(c))
    return bytes(i ^ j for i, j in zip(c, z_stream))

def negacyclic_row(h, i):
    row = [0] * N
    for j in range(N):
        if j + i < N:
            row[j + i] = (row[j + i] + h[j]) % Q
        else:
            row[j + i - N] = (row[j + i - N] - h[j]) % Q
    return row

def solve_instance(idx):
    h = HS[idx]
    c_enc = CS[idx]
    
    M = IntegerMatrix(2 * N, 2 * N)
    for i in range(N):
        M[i, i] = Q
    for i in range(N):
        row = negacyclic_row(h, i)
        for j in range(N):
            M[N + i, j] = row[j]
        M[N + i, N + i] = 1

    LLL.reduction(M)
    BKZ.reduction(M, BKZ.Param(block_size=15))
    
    for i in range(2 * N):
        row = [M[i, j] for j in range(2 * N)]
        if sum(x**2 for x in row) == 160:
            b = row[:N]
            a = row[N:]
            try:
                m = dc(a, b, h, c_enc)
                return idx, m
            except Exception:
                try:
                    m = dc([-x for x in a], [-x for x in b], h, c_enc)
                    return idx, m
                except Exception:
                    pass
    return idx, None

if __name__ == '__main__':
    with mp.Pool(R) as pool:
        results = pool.map(solve_instance, range(R))

    results.sort(key=lambda x: x[0])
    ms = [r[1] for r in results]

    acc = [0] * len(ms[0])
    for idx in range(R - 1):
        acc = [i ^ j for i, j in zip(acc, ms[idx])]

    flag = bytes(i ^ j for i, j in zip(acc, ms[R - 1]))
    print('FLAG:', flag.decode('utf-8'))
