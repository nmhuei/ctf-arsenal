#!/usr/bin/env python3
import os, re, sys, math, socket, subprocess, shutil, time
np = None
from secrets import randbelow

# Challenge parameters: NIST P-256
p = 2**256 - 2**224 + 2**192 + 2**96 - 1
a = -3
b_p256 = 41058363725152142129326129780047268409114441015993725554835256314039467401291
n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
Gx = 48439561293906451759052585252797914202762949526041747995844080717082404635286
Gy = 36134250956749795798585127919587881956611106672985015071877198253568414405109
G = (Gx, Gy)
INF = None

quotes = [
    "Konpeko, konpeko, konpeko! Hololive san-kisei no Usada Pekora-peko! domo, domo!",
    "Bun bun cha! Bun bun cha!",
    "kitira!",
    "usopeko deshou",
    "HA↑HA↑HA↓HA↓HA↓",
    "HA↑HA↑HA↑HA↑",
    "it's me pekora!",
    "ok peko",
]
quote_bytes = [q.encode()[:64].ljust(64, b"\0") for q in quotes]

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def point_to_bytes(P):
    x, y = P
    return x.to_bytes(32, 'big') + y.to_bytes(32, 'big')

def bytes_to_point(bs):
    return (int.from_bytes(bs[:32], 'big'), int.from_bytes(bs[32:], 'big'))

# ---------- basic affine EC for invalid/small work ----------
def ec_add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        return ec_double(P)
    l = ((y2 - y1) * pow((x2 - x1) % p, -1, p)) % p
    x3 = (l*l - x1 - x2) % p
    y3 = (l*(x1 - x3) - y1) % p
    return (x3, y3)

def ec_double(P):
    if P is None: return None
    x, y = P
    if y % p == 0: return None
    l = ((3*x*x + a) * pow((2*y) % p, -1, p)) % p
    x3 = (l*l - 2*x) % p
    y3 = (l*(x - x3) - y) % p
    return (x3, y3)

def ec_neg(P):
    if P is None: return None
    x, y = P
    return (x, (-y) % p)

def ec_mul(k, P):
    if k < 0: return ec_mul(-k, ec_neg(P))
    R = None
    Q = P
    while k:
        if k & 1:
            R = ec_add(R, Q)
        Q = ec_double(Q)
        k >>= 1
    return R

# ---------- faster Jacobian EC for the final small interval ----------
def jac_from_aff(P):
    if P is None: return (0, 1, 0)
    return (P[0], P[1], 1)

def aff_from_jac(P):
    X, Y, Z = P
    if Z == 0: return None
    Zi = pow(Z, -1, p)
    Zi2 = (Zi * Zi) % p
    x = (X * Zi2) % p
    y = (Y * Zi2 * Zi) % p
    return (x, y)

def jac_double(P):
    X1, Y1, Z1 = P
    if Z1 == 0 or Y1 == 0:
        return (0, 1, 0)
    # Formula dbl-2001-b for a=-3
    delta = (Z1 * Z1) % p
    gamma = (Y1 * Y1) % p
    beta = (X1 * gamma) % p
    alpha = (3 * ((X1 - delta) % p) * ((X1 + delta) % p)) % p
    X3 = (alpha * alpha - 8 * beta) % p
    Z3 = ((Y1 + Z1) * (Y1 + Z1) - gamma - delta) % p
    Y3 = (alpha * ((4 * beta - X3) % p) - 8 * gamma * gamma) % p
    return (X3, Y3, Z3)

def jac_add_mixed(P, Q):
    # P Jacobian, Q affine
    if Q is None:
        return P
    X1, Y1, Z1 = P
    if Z1 == 0:
        return (Q[0], Q[1], 1)
    x2, y2 = Q
    Z1Z1 = (Z1 * Z1) % p
    U2 = (x2 * Z1Z1) % p
    S2 = (y2 * Z1 * Z1Z1) % p
    H = (U2 - X1) % p
    HH = (H * H) % p
    if H == 0:
        if (S2 - Y1) % p == 0:
            return jac_double(P)
        return (0, 1, 0)
    I = (4 * HH) % p
    J = (H * I) % p
    r = (2 * (S2 - Y1)) % p
    V = (X1 * I) % p
    X3 = (r * r - J - 2 * V) % p
    Y3 = (r * ((V - X3) % p) - 2 * Y1 * J) % p
    Z3 = (((Z1 + H) * (Z1 + H) - Z1Z1 - HH)) % p
    return (X3, Y3, Z3)

def jac_mul(k, P):
    if k < 0:
        return jac_mul(-k, ec_neg(P))
    R = (0, 1, 0)
    Q = jac_from_aff(P)
    while k:
        if k & 1:
            # add Q (Jacobian) to R: use generic via affine for simplicity in scalar setup only
            R = jac_add_affine(R, aff_from_jac(Q))
        Q = jac_double(Q)
        k >>= 1
    return R

def jac_add_affine(P, Qaff):
    return jac_add_mixed(P, Qaff)

def batch_affine(jpoints):
    npts = len(jpoints)
    prefix = [1] * npts
    acc = 1
    for i, (_, _, Z) in enumerate(jpoints):
        prefix[i] = acc
        if Z:
            acc = (acc * Z) % p
    invacc = pow(acc, -1, p)
    out = [None] * npts
    for i in range(npts-1, -1, -1):
        X, Y, Z = jpoints[i]
        if Z == 0:
            out[i] = None
        else:
            Zi = (invacc * prefix[i]) % p
            invacc = (invacc * Z) % p
            Zi2 = (Zi * Zi) % p
            out[i] = ((X * Zi2) % p, (Y * Zi2 * Zi) % p)
    return out

def point_key(P):
    if P is None:
        return -1
    x, y = P
    return (x << 1) | (y & 1)

def bsgs_interval_ec(base, target, bound, chunk=8192):
    # solve k*base = target, 0 <= k <= bound
    m = math.isqrt(bound) + 1
    print(f"[*] final BSGS interval bound={bound} m={m}", file=sys.stderr)
    table = {}
    cur = (0, 1, 0)  # 0*base
    base_aff = base
    j = 0
    t0 = time.time()
    while j < m:
        cnt = min(chunk, m - j)
        pts = []
        for _ in range(cnt):
            pts.append(cur)
            cur = jac_add_mixed(cur, base_aff)
        affs = batch_affine(pts)
        for off, Paff in enumerate(affs):
            table[point_key(Paff)] = j + off
        j += cnt
        if j % (chunk * 64) == 0:
            print(f"    baby {j}/{m}", file=sys.stderr)
    giant_step = ec_neg(aff_from_jac(jac_mul(m, base_aff)))
    cur = jac_from_aff(target)
    max_i = (bound + m) // m + 1
    for i in range(max_i):
        if i % 64 == 0:
            Paff = aff_from_jac(cur)
            kk = table.get(point_key(Paff))
            if kk is not None:
                ans = i * m + kk
                if ans <= bound and ec_mul(ans, base_aff) == target:
                    print(f"[*] final BSGS hit after {time.time()-t0:.1f}s", file=sys.stderr)
                    return ans
            # Process a small chunk with batch normalization for speed
            pts = []
            ccur = cur
            cnt = min(64, max_i - i)
            for _ in range(cnt):
                pts.append(ccur)
                ccur = jac_add_mixed(ccur, giant_step)
            affs = batch_affine(pts)
            for off, Paff in enumerate(affs):
                kk = table.get(point_key(Paff))
                if kk is not None:
                    ans = (i + off) * m + kk
                    if ans <= bound and ec_mul(ans, base_aff) == target:
                        print(f"[*] final BSGS hit after {time.time()-t0:.1f}s", file=sys.stderr)
                        return ans
            # advance cur by cnt giant steps
            cur = ccur
            if i % (64*256) == 0 and i:
                print(f"    giant {i}/{max_i}", file=sys.stderr)
    raise ValueError("interval dlog not found")

# ---------- Fp2 for nonsplit singular curve y^2=(x-1)^2(x+2) ----------
class Fp2:
    __slots__ = ('a', 'b')
    # a + b*s, s^2 = 3
    def __init__(self, aa, bb=0):
        self.a = aa % p
        self.b = bb % p
    def __add__(self, o):
        o = to2(o); return Fp2(self.a + o.a, self.b + o.b)
    __radd__ = __add__
    def __sub__(self, o):
        o = to2(o); return Fp2(self.a - o.a, self.b - o.b)
    def __rsub__(self, o):
        return to2(o) - self
    def __neg__(self):
        return Fp2(-self.a, -self.b)
    def __mul__(self, o):
        o = to2(o)
        return Fp2(self.a*o.a + 3*self.b*o.b, self.a*o.b + self.b*o.a)
    __rmul__ = __mul__
    def inv(self):
        den = (self.a*self.a - 3*self.b*self.b) % p
        di = pow(den, -1, p)
        return Fp2(self.a * di, -self.b * di)
    def __truediv__(self, o):
        return self * to2(o).inv()
    def __pow__(self, e):
        if e < 0:
            return (self.inv()) ** (-e)
        r = Fp2(1, 0)
        b = self
        while e:
            if e & 1:
                r = r * b
            b = b * b
            e >>= 1
        return r
    def __eq__(self, o):
        o = to2(o); return self.a == o.a and self.b == o.b
    def __hash__(self):
        return hash((self.a, self.b))
    def __repr__(self):
        return f"Fp2({self.a},{self.b})"

def to2(o):
    if isinstance(o, Fp2): return o
    return Fp2(o, 0)

ONE2 = Fp2(1, 0)
S3 = Fp2(0, 1)  # sqrt(3)

def split_point_from_t(t):
    # curve b=-2: y^2=(x+1)^2(x-2), sqrt(-3) in Fp
    s = sqrt_m3
    v = (s * ((t + 1) % p) * pow((t - 1) % p, -1, p)) % p
    x = (v*v + 2) % p
    y = (v * (v*v + 3)) % p
    return (x, y)

def split_t_from_point(P):
    x, y = P
    if (y*y - ((x+1)*(x+1)*(x-2))) % p != 0:
        return None
    if (x + 1) % p == 0:
        return None
    v = y * pow((x + 1) % p, -1, p) % p
    return ((v + sqrt_m3) * pow((v - sqrt_m3) % p, -1, p)) % p

def nonsplit_point_from_t(t):
    # curve b=+2: y^2=(x-1)^2(x+2), sqrt(3) in Fp2
    v = S3 * (t + 1) / (t - 1)
    if v.b != 0:
        raise ValueError('v is not in Fp')
    vv = v.a
    x = (vv*vv - 2) % p
    y = (vv * (vv*vv - 3)) % p
    return (x, y)

def nonsplit_t_from_point(P):
    x, y = P
    if (y*y - ((x-1)*(x-1)*(x+2))) % p != 0:
        return None
    if (x - 1) % p == 0:
        return None
    v = y * pow((x - 1) % p, -1, p) % p
    return (Fp2(v, 0) + S3) / (Fp2(v, 0) - S3)

# ---------- discrete logs in smooth groups ----------
def bsgs_int(g, h, order):
    if order == 1: return 0
    if order == 2:
        return 0 if h == 1 else 1
    m = math.isqrt(order) + 1
    table = {}
    cur = 1
    for j in range(m):
        if cur not in table:
            table[cur] = j
        cur = (cur * g) % p
    factor = pow(pow(g, m, p), -1, p)
    cur = h
    for i in range(m+1):
        j = table.get(cur)
        if j is not None:
            x = i*m + j
            if x < order and pow(g, x, p) == h:
                return x
        cur = (cur * factor) % p
    raise ValueError('bsgs_int failed')

def _mix64(x):
    x &= (1 << 64) - 1
    x ^= x >> 30
    x = (x * 0xbf58476d1ce4e5b9) & ((1 << 64) - 1)
    x ^= x >> 27
    x = (x * 0x94d049bb133111eb) & ((1 << 64) - 1)
    x ^= x >> 31
    return x & ((1 << 64) - 1)

def fp2_fingerprint(e):
    # 64-bit randomized-looking fingerprint from all limbs; verified on hit.
    return (_mix64(e.a) ^ _mix64(e.a >> 64) ^ _mix64(e.a >> 128) ^ _mix64(e.a >> 192) ^
            _mix64(e.b + 0x9e3779b97f4a7c15) ^ _mix64(e.b >> 64) ^
            _mix64(e.b >> 128) ^ _mix64(e.b >> 192)) & ((1 << 64) - 1)

def bsgs_fp2_numpy(g, h, order):
    # Memory-heavy but fast BSGS for the single 46-bit prime factor.
    # Store a 64-bit fingerprint; rare collisions are kept and verified.
    m = math.isqrt(order) + 1
    print(f"[*] large Fp2 BSGS order={order}, m={m}", file=sys.stderr)
    table = {}
    ga, gb = g.a, g.b
    ca, cb = 1, 0
    MASK64 = (1 << 64) - 1
    t0 = time.time()
    for j in range(m):
        key = ca & MASK64
        old = table.get(key)
        if old is None:
            table[key] = j
        elif isinstance(old, list):
            old.append(j)
        else:
            table[key] = [old, j]
        ca, cb = (ca*ga + 3*cb*gb) % p, (ca*gb + cb*ga) % p
        if j and j % 1000000 == 0:
            print(f"    large baby {j}/{m}", file=sys.stderr)
    factor = (g ** m).inv()
    fa, fb = factor.a, factor.b
    ca, cb = h.a, h.b
    for i in range(m + 1):
        got = table.get(ca & MASK64)
        if got is not None:
            js = got if isinstance(got, list) else [got]
            for j in js:
                x = i*m + j
                if x < order and (g ** x) == h:
                    print(f"[*] large Fp2 BSGS hit after {time.time()-t0:.1f}s", file=sys.stderr)
                    return x
        ca, cb = (ca*fa + 3*cb*fb) % p, (ca*fb + cb*fa) % p
        if i and i % 1000000 == 0:
            print(f"    large giant {i}/{m}", file=sys.stderr)
    raise ValueError('large Fp2 BSGS failed')

def bsgs_fp2(g, h, order):
    if order == 1: return 0
    if order == 2:
        return 0 if h == ONE2 else 1
    if order > 10**9:
        return bsgs_fp2_numpy(g, h, order)
    m = math.isqrt(order) + 1
    table = {}
    cur = ONE2
    for j in range(m):
        if cur not in table:
            table[cur] = j
        cur = cur * g
    factor = (g ** m).inv()
    cur = h
    for i in range(m+1):
        j = table.get(cur)
        if j is not None:
            x = i*m + j
            if x < order and (g ** x) == h:
                return x
        cur = cur * factor
    raise ValueError('bsgs_fp2 failed')

def crt_pair(a1, m1, a2, m2):
    # coprime
    t = ((a2 - a1) % m2) * pow(m1 % m2, -1, m2) % m2
    return (a1 + m1*t) % (m1*m2), m1*m2

def crt_list(congruences):
    x, m = 0, 1
    for ai, mi in congruences:
        x, m = crt_pair(x, m, ai % mi, mi)
    return x, m

def pohlig_hellman_int(g, h, N, factors):
    congr = []
    for q, e in factors.items():
        qe = q**e
        gamma = pow(g, N//q, p)
        x = 0
        for j in range(e):
            c = (h * pow(pow(g, x, p), -1, p)) % p
            c = pow(c, N // (q**(j+1)), p)
            aj = bsgs_int(gamma, c, q)
            x += aj * (q**j)
        print(f"[*] PH split: mod {qe} -> {x}", file=sys.stderr)
        congr.append((x, qe))
    return crt_list(congr)

def pohlig_hellman_fp2(g, h, N, factors):
    congr = []
    for q, e in factors.items():
        qe = q**e
        gamma = g ** (N//q)
        x = 0
        for j in range(e):
            c = h * (g ** x).inv()
            c = c ** (N // (q**(j+1)))
            aj = bsgs_fp2(gamma, c, q)
            x += aj * (q**j)
        print(f"[*] PH nonsplit: mod {qe} -> {x}", file=sys.stderr)
        congr.append((x, qe))
    return crt_list(congr)

# ---------- IO ----------
class Conn:
    def __init__(self, mode, host=None, port=None, workdir=None):
        self.mode = mode
        if mode == 'remote':
            self.s = socket.create_connection((host, port), timeout=20)
            self.s.settimeout(20)
        else:
            env = os.environ.copy()
            env['FLAG'] = env.get('FLAG', 'AIS3{local_test_flag_peko}')
            self.p = subprocess.Popen([sys.executable, 'server.py'], cwd=workdir, env=env,
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    def read1(self):
        if self.mode == 'remote':
            return self.s.recv(1)
        c = self.p.stdout.read(1)
        return c
    def send(self, data):
        if isinstance(data, str): data = data.encode()
        if self.mode == 'remote':
            self.s.sendall(data)
        else:
            self.p.stdin.write(data); self.p.stdin.flush()
    def read_until(self, token):
        if isinstance(token, str): token = token.encode()
        buf = b''
        while not buf.endswith(token):
            c = self.read1()
            if not c:
                raise EOFError(buf.decode(errors='ignore'))
            buf += c
        return buf
    def close(self):
        try:
            if self.mode == 'remote': self.s.close()
            else: self.p.kill()
        except Exception: pass

def parse_public_key(buf):
    m = re.search(rb'public key: \((\d+), (\d+)\)', buf)
    if not m:
        raise ValueError('public key not found')
    return (int(m.group(1)), int(m.group(2)))

def oracle_dh(conn, Q, mapper, order):
    conn.send('1\n')
    conn.read_until('x: ')
    conn.send(str(Q[0]) + '\n')
    conn.read_until('y: ')
    conn.send(str(Q[1]) + '\n')
    out = conn.read_until('> ')
    # print(out.decode(errors='ignore'), file=sys.stderr)
    hs = re.findall(rb'\b[0-9a-f]{128}\b', out)
    if not hs:
        raise ValueError('no ciphertext in oracle response: ' + out.decode(errors='ignore'))
    c = bytes.fromhex(hs[0].decode())
    candidates = []
    for qb in quote_bytes:
        kb = xor(c, qb)
        P = bytes_to_point(kb)
        t = mapper(P)
        if t is None:
            continue
        # subgroup check
        ok = (pow(t, order, p) == 1) if isinstance(t, int) else ((t ** order) == ONE2)
        if ok:
            candidates.append((P, t))
    if len(candidates) != 1:
        raise ValueError(f'ambiguous oracle decode: {len(candidates)} candidates')
    return candidates[0]

def get_flag_cipher(conn):
    conn.send('2\n')
    out = conn.read_until('> ')
    hs = re.findall(rb'\b[0-9a-f]+\b', out)
    # Need exactly two long hex strings: C1(128), C2(128)
    longs = [h for h in hs if len(h) == 128]
    if len(longs) < 2:
        raise ValueError('flag ciphertext parse failed: ' + out.decode(errors='ignore'))
    C1 = bytes_to_point(bytes.fromhex(longs[0].decode()))
    C2 = bytes.fromhex(longs[1].decode())
    return C1, C2

# ---------- attack setup ----------
sqrt_m3 = pow((-3) % p, (p + 1)//4, p)
assert (sqrt_m3 * sqrt_m3) % p == (-3) % p

fac_split = {3:1, 5:2, 17:1, 257:1, 641:1, 1531:1, 65537:1, 490463:1, 6700417:1}
M_split = math.prod(q**e for q, e in fac_split.items())
fac_nonsplit = {2:96, 7:1, 274177:1, 67280421310721:1}
M_nonsplit = math.prod(q**e for q, e in fac_nonsplit.items())

def find_split_t():
    for h in range(2, 1000):
        t = pow(h, (p-1)//M_split, p)
        if t != 1 and all(pow(t, M_split//q, p) != 1 for q in fac_split):
            return t
    raise ValueError('split element not found')

def find_nonsplit_t():
    for aa in range(2, 100):
        for bb in range(1, 100):
            z = Fp2(aa, bb)
            u = z ** (p-1)           # norm-one subgroup, order | p+1
            t = u ** ((p+1)//M_nonsplit)
            if t != ONE2 and all((t ** (M_nonsplit//q)) != ONE2 for q in fac_nonsplit):
                return t
    raise ValueError('nonsplit element not found')

def attack(conn):
    banner = conn.read_until('> ')
    Ppub = parse_public_key(banner)
    print(f"[*] public key parsed", file=sys.stderr)

    # 1) split singular curve b=-2, order divides p-1
    t1 = find_split_t()
    Q1 = split_point_from_t(t1)
    print(f"[*] querying split singular subgroup, M={M_split}", file=sys.stderr)
    _, h1 = oracle_dh(conn, Q1, split_t_from_point, M_split)
    d1, m1 = pohlig_hellman_int(t1, h1, M_split, fac_split)
    print(f"[*] d mod M_split = {d1}", file=sys.stderr)

    # 2) nonsplit singular curve b=+2, smooth part of p+1
    t2 = find_nonsplit_t()
    Q2 = nonsplit_point_from_t(t2)
    print(f"[*] querying nonsplit singular subgroup, M={M_nonsplit}", file=sys.stderr)
    _, h2 = oracle_dh(conn, Q2, nonsplit_t_from_point, M_nonsplit)
    d2, m2 = pohlig_hellman_fp2(t2, h2, M_nonsplit, fac_nonsplit)
    print(f"[*] d mod M_nonsplit = {d2}", file=sys.stderr)

    d, M = crt_list([(d1, m1), (d2, m2)])
    print(f"[*] CRT modulus bits={M.bit_length()}", file=sys.stderr)
    if M <= n:
        # Fallback kept for experimentation; normally the large nonsplit factor makes M > n.
        if d >= n:
            raise ValueError('CRT residue unexpectedly >= n')
        H = ec_add(Ppub, ec_neg(ec_mul(d, G)))
        B = ec_mul(M, G)
        bound = (n - 1 - d) // M
        k = bsgs_interval_ec(B, H, bound)
        d = d + k*M
    if d >= n or ec_mul(d, G) != Ppub:
        raise ValueError('recovered d failed public-key check')
    print(f"[*] recovered d = {d}", file=sys.stderr)

    C1, C2 = get_flag_cipher(conn)
    S = ec_mul(d, C1)
    flag_padded = xor(C2, point_to_bytes(S))
    flag = flag_padded.split(b'}', 1)[0] + b'}'
    return flag, d

def prepare_local(srcdir):
    wd = '/tmp/pekobot_local'
    os.makedirs(wd, exist_ok=True)
    srv = open(os.path.join(srcdir, 'server_d89bd2a8f60775be9d7c287b000b5241.py')).read()
    srv = srv.replace('from Crypto.Util.number import bytes_to_long\n', '')
    open(os.path.join(wd, 'server.py'), 'w').write(srv)
    shutil.copy(os.path.join(srcdir, 'elliptic_curve_52f6bc65c648473827df6824b1fb103a.py'), os.path.join(wd, 'elliptic_curve.py'))
    return wd

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'local'
    if mode == 'local':
        srcdir = sys.argv[2] if len(sys.argv) > 2 else '/mnt/data/pekobot/pekobot-ais3-pre-exam/files'
        wd = prepare_local(srcdir)
        c = Conn('local', workdir=wd)
    elif mode == 'remote':
        host = sys.argv[2] if len(sys.argv) > 2 else 'archive.cryptohack.org'
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 45328
        c = Conn('remote', host, port)
    else:
        print('usage: solve_pekobot.py [local [filesdir] | remote host port]')
        sys.exit(1)
    try:
        flag, d = attack(c)
        print(flag.decode(errors='replace'))
    finally:
        c.close()
