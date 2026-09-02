#!/usr/bin/env python3
import base64, gzip, ast, random, re, socket, sys
from sympy import Matrix

q = 8380417
N = 256
k, l = 8, 7
eta = 2

# ---------- challenge-compatible codec ----------
def decode_obj(s):
    return ast.literal_eval(gzip.decompress(base64.b64decode(s)).decode())

def encode_obj(obj):
    raw = str(obj).replace(' ', '').encode()
    return base64.b64encode(gzip.compress(raw)).decode()

# ---------- X=1 projection ----------
def eval1(poly):
    return sum(int(x) for x in poly) % q

def project_instance(A, t):
    A1 = [[eval1(A[i][j]) for j in range(l)] for i in range(k)]
    t1 = [eval1(t[i]) for i in range(k)]
    return A1, t1

# ---------- Babai CVP after LLL ----------
def babai_closest_vector(rows, target):
    Bm = Matrix(rows).lll()
    B = [[int(Bm[i, j]) for j in range(Bm.cols)] for i in range(Bm.rows)]
    n = len(B)
    dim = len(B[0])

    bstar = []
    norms = []
    for i in range(n):
        v = [float(x) for x in B[i]]
        for j in range(i):
            mu = sum(B[i][p] * bstar[j][p] for p in range(dim)) / norms[j]
            for p in range(dim):
                v[p] -= mu * bstar[j][p]
        norm = sum(x * x for x in v)
        if norm == 0:
            raise ValueError('dependent lattice basis')
        bstar.append(v)
        norms.append(norm)

    y = [float(x) for x in target]
    coeffs = [0] * n
    for i in reversed(range(n)):
        c = sum(y[p] * bstar[i][p] for p in range(dim)) / norms[i]
        z = round(c)
        coeffs[i] = z
        for p in range(dim):
            y[p] -= z * B[i][p]

    close = [0] * dim
    for z, row in zip(coeffs, B):
        if z:
            for p in range(dim):
                close[p] += z * row[p]
    return close

def score_projected(A1, t1):
    # Lattice L = {(s, A*s + q*c) : s in Z^7, c in Z^8}
    # Target is (0, t).  For MLWE, a close vector gives difference (s, -e).
    rows = []
    for j in range(l):
        row = [0] * (l + k)
        row[j] = 1
        for i in range(k):
            row[l + i] = A1[i][j]
        rows.append(row)
    for i in range(k):
        row = [0] * (l + k)
        row[l + i] = q
        rows.append(row)

    target = [0] * l + t1
    close = babai_closest_vector(rows, target)
    diff = [close[i] - target[i] for i in range(l + k)]
    return max(abs(x) for x in diff), sum(x * x for x in diff), diff

def distinguish(A, t, threshold=1000):
    A1, t1 = project_instance(A, t)
    mx, _, _ = score_projected(A1, t1)
    return int(mx < threshold)

# ---------- local simulator, no Sage needed ----------
def rand_small_poly():
    return [random.randint(-eta, eta) for _ in range(N)]

def rand_uniform_poly():
    return [random.randrange(q) for _ in range(N)]

def cyclic_mul(a, b):
    out = [0] * N
    # b is tiny in MLWE generation, so skip zeros
    for j, bj in enumerate(b):
        if bj:
            for i, ai in enumerate(a):
                out[(i + j) & (N - 1)] = (out[(i + j) & (N - 1)] + ai * bj) % q
    return out

def local_instance():
    is_mlwe = random.getrandbits(1)
    A = [[rand_uniform_poly() for _ in range(l)] for __ in range(k)]
    if is_mlwe:
        s = [rand_small_poly() for _ in range(l)]
        e = [rand_small_poly() for _ in range(k)]
        t = []
        for i in range(k):
            acc = [0] * N
            for j in range(l):
                prod = cyclic_mul(A[i][j], s[j])
                for c in range(N):
                    acc[c] = (acc[c] + prod[c]) % q
            for c in range(N):
                acc[c] = (acc[c] + e[i][c]) % q
            t.append(acc)
    else:
        t = [rand_uniform_poly() for _ in range(k)]
    return A, t, is_mlwe

def local_projected_instance():
    # Exact distribution after evaluating at X=1.
    # Sum of 256 uniform coefficients is uniform mod q.
    bit = random.getrandbits(1)
    A1 = [[random.randrange(q) for _ in range(l)] for __ in range(k)]
    if bit:
        s1 = [sum(random.randint(-eta, eta) for _ in range(N)) for __ in range(l)]
        e1 = [sum(random.randint(-eta, eta) for _ in range(N)) for __ in range(k)]
        t1 = [(sum(A1[i][j] * s1[j] for j in range(l)) + e1[i]) % q for i in range(k)]
    else:
        t1 = [random.randrange(q) for _ in range(k)]
    return A1, t1, bit

def selftest(rounds=130):
    ok = 0
    mlwe_scores, rand_scores = [], []
    for r in range(rounds):
        A1, t1, bit = local_projected_instance()
        mx, _, _ = score_projected(A1, t1)
        guess = int(mx < 1000)
        ok += (guess == bit)
        (mlwe_scores if bit else rand_scores).append(mx)
        print(f'{r+1:03d}: score={mx:5d} guess={guess} real={bit} ok={ok}')
    print(f'\nlocal result: {ok}/{rounds}')
    if mlwe_scores:
        print(f'MLWE score range:   {min(mlwe_scores)}..{max(mlwe_scores)}')
    if rand_scores:
        print(f'random score range: {min(rand_scores)}..{max(rand_scores)}')

# ---------- one-shot solve for captured sanitized strings ----------
def solve_sanitized(Aenc, tenc):
    A = decode_obj(Aenc)
    t = decode_obj(tenc)
    return distinguish(A, t)

def parse_sanitized_line(line, name):
    prefix = f'{name} = '
    if not line.startswith(prefix):
        raise ValueError(f'expected {prefix!r}, got {line!r}')
    return ast.literal_eval(line[len(prefix):])

def recv_line(sockfile):
    line = sockfile.readline()
    if not line:
        return None
    return line.decode(errors='replace').rstrip('\n')

def solve_remote(host, port, verbose=False):
    with socket.create_connection((host, int(port)), timeout=15) as sock:
        sockfile = sock.makefile('rwb', buffering=0)
        Aenc = None
        rounds = 0

        while True:
            line = recv_line(sockfile)
            if line is None:
                break

            if line.startswith('Well played, here is the flag'):
                print(line)
                return 0
            if verbose or not line.startswith(('sanitize_mat(A) = ', 'sanitize_vec(t) = ')):
                print(line)
            if line.startswith('sanitize_mat(A) = '):
                Aenc = parse_sanitized_line(line, 'sanitize_mat(A)')
                continue
            if line.startswith('sanitize_vec(t) = '):
                if Aenc is None:
                    raise ValueError('received vector before matrix')
                tenc = parse_sanitized_line(line, 'sanitize_vec(t)')
                guess = solve_sanitized(Aenc, tenc)
                rounds += 1

                prompt = recv_line(sockfile)
                if prompt is None:
                    break
                if verbose:
                    print(prompt)
                if prompt != 'MLWE (1) or not (0) ?':
                    raise ValueError(f'unexpected prompt line: {prompt!r}')

                print(f'[solver] round {rounds}: answer={guess}', file=sys.stderr)
                sockfile.write(f'{guess}\n'.encode())
                Aenc = None

        return 1

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] == '--selftest':
        rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 130
        selftest(rounds)
    elif len(sys.argv) in (4, 5) and sys.argv[1] == '--remote':
        verbose = len(sys.argv) == 5 and sys.argv[4] == '--verbose'
        if len(sys.argv) == 5 and not verbose:
            print('unknown option:', sys.argv[4])
            sys.exit(1)
        sys.exit(solve_remote(sys.argv[2], sys.argv[3], verbose))
    elif len(sys.argv) == 3:
        print(solve_sanitized(sys.argv[1], sys.argv[2]))
    else:
        print('usage: python3 local_eyes_solver.py [--selftest 130]')
        print('   or: python3 local_eyes_solver.py --remote <host> <port> [--verbose]')
        print('   or: python3 local_eyes_solver.py <sanitize_mat(A)> <sanitize_vec(t)>')
        sys.exit(1)
