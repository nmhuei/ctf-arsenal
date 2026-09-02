#!/usr/bin/env python3
import os, sys, math, random, socket, subprocess, time, itertools
from pathlib import Path

q = 2**128 - 159
a = 1
b = 1494
E_ORDER = 340282366920938463465004184633952524077
TWIST_ORDER = 2*(q+1) - E_ORDER
FACTORS = [3, 79, 644899, 1283505703, 19385376821, 89480282251]
# sorted roughly small->large; all prime and product = TWIST_ORDER

# challenge x-only functions, for validation and optional local direct oracle
def xDBLADD(P, Q, PQ):
    (X1, Z1), (X2, Z2), (X3, Z3) = PQ, P, Q
    X4 = (X2**2 - a * Z2**2) ** 2 - 8 * b * X2 * Z2**3
    Z4 = 4 * (X2 * Z2 * (X2**2 + a * Z2**2) + b * Z2**4)
    X5 = Z1 * ((X2 * X3 - a * Z2 * Z3) ** 2 - 4 * b * Z2 * Z3 * (X2 * Z3 + X3 * Z2))
    Z5 = X1 * (X2 * Z3 - X3 * Z2) ** 2
    X4, Z4, X5, Z5 = (c % q for c in (X4, Z4, X5, Z5))
    return (X4, Z4), (X5, Z5)

def xMUL(P, k):
    Q, R = (1, 0), P
    for i in reversed(range(k.bit_length() + 1)):
        if k >> i & 1:
            R, Q = Q, R
        Q, R = xDBLADD(Q, R, P)
        if k >> i & 1:
            R, Q = Q, R
    return Q

def xmul_affine(x, k):
    X,Z = xMUL((x % q, 1), k)
    if Z == 0:
        return None
    return X * pow(Z, -1, q) % q

def f(x):
    return (x*x % q * x + a*x + b) % q

def legendre(x):
    if x % q == 0:
        return 0
    r = pow(x % q, (q-1)//2, q)
    return -1 if r == q-1 else r

def find_nonsquare():
    z = 2
    while legendre(z) != -1:
        z += 1
    return z

C = find_nonsquare()

def modsqrt(n):
    """Tonelli-Shanks modulo q (q prime). Returns one sqrt, or None."""
    n %= q
    if n == 0:
        return 0
    if legendre(n) != 1:
        return None
    # q % 4 shortcut unavailable here (q % 4 == 1), use generic.
    Q = q - 1
    S = 0
    while Q % 2 == 0:
        S += 1
        Q //= 2
    z = 2
    while legendre(z) != -1:
        z += 1
    M = S
    c = pow(z, Q, q)
    t = pow(n, Q, q)
    R = pow(n, (Q + 1) // 2, q)
    while t != 1:
        i = 1
        t2i = (t * t) % q
        while t2i != 1:
            t2i = (t2i * t2i) % q
            i += 1
            if i >= M:
                raise RuntimeError('Tonelli failed')
        b2 = pow(c, 1 << (M - i - 1), q)
        M = i
        c = (b2 * b2) % q
        t = (t * c) % q
        R = (R * b2) % q
    return R

# Twist model: C*Y^2 = x^3 + a*x + b.
# It is the anti-invariant subgroup of E(F_q^2); x coords match the x-only ladder.
def twist_lift_x(x):
    rhs = f(x)
    y2 = rhs * pow(C, -1, q) % q
    y = modsqrt(y2)
    if y is None:
        return None
    return (x % q, y)

def neg(P):
    if P is None:
        return None
    x,y = P
    return (x, (-y) % q)

def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1,y1 = P
    x2,y2 = Q
    if x1 == x2:
        if (y1 + y2) % q == 0:
            return None
        # lambda = s*L in E(Fq^2), L=(3*x^2+a)/(2*C*y)
        L = (3*x1*x1 + a) * pow((2*C*y1) % q, -1, q) % q
    else:
        L = (y2 - y1) * pow((x2 - x1) % q, -1, q) % q
    x3 = (C * L * L - x1 - x2) % q
    y3 = (L * (x1 - x3) - y1) % q
    return (x3, y3)

def mul(P, k):
    if k < 0:
        return mul(neg(P), -k)
    R = None
    A = P
    while k:
        if k & 1:
            R = add(R, A)
        A = add(A, A)
        k >>= 1
    return R

def point_key(P):
    return None if P is None else (P[0], P[1])

def bsgs_xonly(P, target_x, order):
    """Return k with x(kP)=target_x; sign may be +/- true scalar modulo order."""
    Q = twist_lift_x(target_x)
    if Q is None:
        raise ValueError('target is not on twist')
    m = math.isqrt(order) + 1
    table = {}
    R = None
    for j in range(m):
        # For order 2 not relevant. Store both? We solve exact chosen Q; sign ambiguity handled by lift.
        table.setdefault(point_key(R), j)
        R = add(R, P)
    mP = mul(P, m)
    neg_mP = neg(mP)
    gamma = Q
    for i in range(m + 1):
        j = table.get(point_key(gamma))
        if j is not None:
            return (i*m + j) % order
        gamma = add(gamma, neg_mP)
    # try the other lift explicitly, though it should equal -k case
    gamma = neg(Q)
    for i in range(m + 1):
        j = table.get(point_key(gamma))
        if j is not None:
            return (i*m + j) % order
        gamma = add(gamma, neg_mP)
    raise ValueError('DLP not found')

def random_twist_point(rng=random):
    while True:
        x = rng.randrange(1, q)
        if legendre(f(x)) == -1:
            P = twist_lift_x(x)
            if P is not None:
                return P

def subgroup_generator(l, rng=random):
    co = TWIST_ORDER // l
    while True:
        P = random_twist_point(rng)
        G = mul(P, co)
        if G is not None and mul(G, l) is None:
            # sanity: x-only ladder should agree for a few multipliers
            return G

def crt_pair(a1, m1, a2, m2):
    # coprime moduli
    t = ((a2 - a1) % m2) * pow(m1 % m2, -1, m2) % m2
    return (a1 + m1*t) % (m1*m2), m1*m2

def combine_residue_sets(residue_sets):
    sols = [(0,1)]
    for mod, vals in residue_sets:
        ns=[]
        for a0,m0 in sols:
            for v in vals:
                ns.append(crt_pair(a0,m0,v,mod))
        # dedup
        d={a:m for a,m in ns}
        sols=[(a,m) for a,m in d.items()]
    return sols

def int_to_bytes_min(n):
    if n == 0:
        return b''
    return n.to_bytes((n.bit_length()+7)//8, 'big')

def score_bytes(bs):
    if not bs:
        return -10
    score=0
    for c in bs:
        if 32 <= c < 127:
            score += 2
        if chr(c) in '{}_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-!?.':
            score += 1
        if c in b'\x00\xff\n\r\t':
            score -= 5
        if c < 32 or c >= 127:
            score -= 4
    # CTF flags often lowercase/underscore
    if all(32 <= c < 127 for c in bs): score += 20
    return score

class DirectOracle:
    def __init__(self, d): self.d=d
    def query(self, x):
        return xmul_affine(x, self.d)  # None means infinity/crash equivalent

class ProcOracle:
    def __init__(self, script_path, flag):
        self.script_path=script_path
        self.flag=flag
    def query(self, x):
        env=os.environ.copy(); env['FLAG']=self.flag
        p=subprocess.Popen([sys.executable, self.script_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True)
        try:
            # prompt has no newline; send one query then read output
            out,err=p.communicate(str(x)+'\n', timeout=5)
        except subprocess.TimeoutExpired:
            p.kill(); out,err=p.communicate()
        lines=[s.strip() for s in out.replace('x-coordinate:','\n').splitlines() if s.strip()]
        for s in reversed(lines):
            if s.isdigit(): return int(s)
        return None

class RemoteOracle:
    def __init__(self, host, port, timeout=7):
        self.host=host; self.port=int(port); self.timeout=timeout
    def query(self, x):
        with socket.create_connection((self.host,self.port), timeout=self.timeout) as s:
            s.settimeout(self.timeout)
            # wait for prompt or just send; service is input() prompt without newline
            data=b''
            try:
                while b'x-coordinate:' not in data and len(data)<200:
                    chunk=s.recv(1)
                    if not chunk: break
                    data += chunk
            except socket.timeout:
                pass
            s.sendall((str(x)+'\n').encode())
            data=b''
            try:
                while True:
                    chunk=s.recv(4096)
                    if not chunk: break
                    data += chunk
                    # one line of output is enough; next prompt may be included
                    if b'\n' in data: break
            except socket.timeout:
                pass
        txt=data.decode(errors='ignore').replace('x-coordinate:', '\n')
        nums=[]
        for tok in txt.replace('\r','\n').split():
            if tok.isdigit(): nums.append(int(tok))
        if nums: return nums[0]
        return None

def recover_mod_twist(oracle, seed=1337, verbose=True):
    rng=random.Random(seed)
    residue_sets=[]
    used=[]
    for l in FACTORS:
        if verbose: print(f'[*] subgroup order {l}', flush=True)
        G = subgroup_generator(l, rng)
        x = G[0]
        # More sanity: G is on twist and order l; xMUL should return infinity for l*G.
        if xmul_affine(x, l) is not None:
            print('[!] x-only order sanity failed', file=sys.stderr)
        y = oracle.query(x)
        if y is None:
            vals=[0]
            if verbose: print(f'    oracle returned infinity/crashed => d = 0 mod {l}', flush=True)
        else:
            k = bsgs_xonly(G, y, l)
            vals=sorted(set([k % l, (-k) % l]))
            if verbose: print(f'    k = ±{k} mod {l}; residues {vals}', flush=True)
        residue_sets.append((l, vals))
        used.append((l,x,vals))
    sols=combine_residue_sets(residue_sets)
    M=1
    for l in FACTORS: M*=l
    assert M == TWIST_ORDER
    cands=[]
    for a,m in sols:
        bs=int_to_bytes_min(a)
        cands.append((score_bytes(bs), a, bs))
    cands.sort(reverse=True, key=lambda t:t[0])
    return cands, used

def gen_secret(flag):
    d = flag.lstrip('ECSC{').rstrip('}')
    return int.from_bytes(d.encode(), 'big')

def selftest():
    assert math.prod(FACTORS) == TWIST_ORDER
    print('[+] q=',q)
    print('[+] nonsquare C=',C)
    # compare twist group law/x-only ladder
    rng=random.Random(1)
    for _ in range(20):
        P=random_twist_point(rng)
        k=rng.randrange(1,10000)
        A=mul(P,k)
        x1=None if A is None else A[0]
        x2=xmul_affine(P[0],k)
        assert x1==x2, (P,k,x1,x2)
    print('[+] twist arithmetic matches x-only ladder')
    fake='ECSC{twist_test_123}'  # 14-byte secret < 2^128
    d=gen_secret(fake)
    cands,_=recover_mod_twist(DirectOracle(d), seed=2, verbose=True)
    print('[+] top candidates:')
    for sc,a,bs in cands[:8]:
        print(sc, a, bs, 'ECSC{'+bs.decode(errors='replace')+'}')
    assert any(bs == b'twist_test_123' for _,_,bs in cands)
    print('[+] local selftest recovered', fake)

def main():
    if len(sys.argv)<2 or sys.argv[1] in ('selftest','local'):
        selftest(); return
    mode=sys.argv[1]
    if mode=='proc':
        if len(sys.argv)<4:
            print('usage: solve_twist.py proc /path/to/twist_and_shout.py ECSC{short_test_flag}')
            sys.exit(1)
        oracle=ProcOracle(sys.argv[2], sys.argv[3])
    elif mode=='remote':
        if len(sys.argv)<4:
            print('usage: solve_twist.py remote host port')
            sys.exit(1)
        oracle=RemoteOracle(sys.argv[2], int(sys.argv[3]))
    else:
        print('modes: selftest|proc|remote')
        sys.exit(1)
    cands,_=recover_mod_twist(oracle, verbose=True)
    print('\n[+] best decoded candidates for d mod twist_order:')
    for sc,a,bs in cands[:20]:
        s=bs.decode(errors='replace')
        print(f'score={sc:4d} d={a}\n    inner={bs!r}\n    flag=ECSC{{{s}}}')

if __name__=='__main__':
    main()
