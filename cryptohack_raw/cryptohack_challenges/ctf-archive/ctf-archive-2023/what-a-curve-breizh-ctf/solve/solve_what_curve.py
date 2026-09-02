#!/usr/bin/env python3
import os
import sys
import socket
import struct
import subprocess
import random
import warnings
from itertools import zip_longest

warnings.filterwarnings("ignore")

try:
    import sympy as sp
    try:
        from sympy.utilities.exceptions import SymPyDeprecationWarning
        warnings.filterwarnings("ignore", category=SymPyDeprecationWarning)
    except Exception:
        pass
except ImportError:
    sp = None

p = 17585255163044402023
SUFFIX = b" This is your final boss, enjoy it while you still can:)"
BLOCK = 14 * 8
HALF = 7 * 8

# ---------- finite-field polynomial helpers, low-to-high coefficients ----------
def trim(a):
    a = [x % p for x in a]
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a

def poly_add(a, b):
    n = max(len(a), len(b))
    return trim([(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)])

def poly_sub(a, b):
    n = max(len(a), len(b))
    return trim([(a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0) for i in range(n)])

def poly_mul(a, b):
    a, b = trim(a), trim(b)
    if a == [0] or b == [0]:
        return [0]
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] = (c[i + j] + x * y) % p
    return trim(c)

def poly_divmod(a, b):
    a, b = trim(a[:]), trim(b[:])
    if b == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    if len(a) < len(b):
        return [0], a
    q = [0] * (len(a) - len(b) + 1)
    inv_lc = pow(b[-1], -1, p)
    while len(a) >= len(b) and a != [0]:
        coef = a[-1] * inv_lc % p
        k = len(a) - len(b)
        q[k] = coef
        for i in range(len(b)):
            a[k + i] = (a[k + i] - coef * b[i]) % p
        a = trim(a)
    return trim(q), trim(a)

def poly_mod(a, m):
    return poly_divmod(a, m)[1]

def xpow_mod(i, m):
    return poly_mod([0] * i + [1], m)

def poly_eval(f, x):
    r = 0
    for c in reversed(f):
        r = (r * x + c) % p
    return r

# ---------- linear algebra over GF(p) ----------
def solve_linear_mod(A, b):
    aug = [[x % p for x in row] + [bb % p] for row, bb in zip(A, b)]
    m = len(aug)
    n = len(aug[0]) - 1
    r = 0
    pivots = []
    for c in range(n):
        pivot = None
        for i in range(r, m):
            if aug[i][c] % p:
                pivot = i
                break
        if pivot is None:
            continue
        aug[r], aug[pivot] = aug[pivot], aug[r]
        inv = pow(aug[r][c] % p, -1, p)
        aug[r] = [(x * inv) % p for x in aug[r]]
        for i in range(m):
            if i != r and aug[i][c] % p:
                fac = aug[i][c] % p
                aug[i] = [(aug[i][j] - fac * aug[r][j]) % p for j in range(n + 1)]
        pivots.append(c)
        r += 1
        if r == n:
            break
    sol = [0] * n
    for row, col in enumerate(pivots):
        sol[col] = aug[row][-1]
    for row, bb in zip(A, b):
        if sum(row[j] * sol[j] for j in range(n)) % p != bb % p:
            raise ValueError("linear system is inconsistent; retry the oracle query")
    return sol

# ---------- challenge-specific algebra ----------
def parse_block(block):
    if len(block) != BLOCK:
        raise ValueError("need a complete 112-byte RNG block")
    vals = list(struct.unpack("<14Q", block))
    return vals[:7], vals[7:]

def recover_curve_f(raw_stream):
    """Recover f from at least three complete known RNG blocks."""
    if len(raw_stream) < 3 * BLOCK:
        raise ValueError("need at least three complete oracle blocks")
    equations = []
    rhs = []
    for off in range(0, 3 * BLOCK, BLOCK):
        ucoef, vcoef = parse_block(raw_stream[off:off + BLOCK])
        u = ucoef + [1]             # Mumford u is monic degree 7.
        v = vcoef
        target = poly_mod(poly_mul(v, v), u) + [0] * 7
        reductions = []
        for i in range(16):
            r = xpow_mod(i, u) + [0] * 7
            reductions.append(r[:7])
        # f(x) == v(x)^2 mod u(x), giving seven linear equations in f_i.
        for k in range(7):
            equations.append([reductions[i][k] for i in range(16)])
            rhs.append(target[k])
    return solve_linear_mod(equations, rhs)

def factor_monic_degree7_divisors(h):
    if sp is None:
        raise RuntimeError("Install sympy first: python3 -m pip install sympy")
    x = sp.symbols("x")
    h = trim(h)
    expr = sum(int(c % p) * x**i for i, c in enumerate(h))
    _, raw_factors = sp.factor_list(expr, modulus=p)
    factors = []
    for fac_expr, exp in raw_factors:
        poly = sp.Poly(fac_expr, x, modulus=p)
        coeffs = [int(c) % p for c in reversed(poly.all_coeffs())]
        inv_lc = pow(coeffs[-1], -1, p)
        coeffs = trim([(c * inv_lc) % p for c in coeffs])
        factors.append((coeffs, exp))

    out = []
    def rec(i, cur):
        deg = len(trim(cur)) - 1
        if deg > 7:
            return
        if i == len(factors):
            cur = trim(cur)
            if len(cur) - 1 == 7 and poly_mod(h, cur) == [0]:
                # cur is monic by construction.
                out.append(cur)
            return
        fac, exp = factors[i]
        power = [1]
        for _ in range(exp + 1):
            rec(i + 1, poly_mul(cur, power))
            power = poly_mul(power, fac)
    rec(0, [1])
    # Deduplicate, preserving order.
    seen = set()
    uniq = []
    for u in out:
        t = tuple(u)
        if t not in seen:
            seen.add(t)
            uniq.append(u)
    return uniq

def score_plaintext(pt):
    score = 0
    if all(32 <= c < 127 for c in pt):
        score += 50
    for pref in (b"crypto{", b"BZHCTF{", b"BreizhCTF{", b"flag{", b"FLAG{", b"CTF{"):
        if pt.startswith(pref):
            score += 200
    if b"{" in pt and b"}" in pt:
        score += 100
    if pt.endswith(b"}"):
        score += 50
    # Penalize obvious binary junk.
    score -= sum(not (9 <= c <= 13 or 32 <= c < 127) for c in pt) * 10
    return score

def recover_flag_from_first_ciphertext(ct, f):
    if len(ct) != BLOCK:
        raise NotImplementedError(
            f"expected len(flag)+len(suffix)=112 bytes, got {len(ct)}. "
            "This official instance is expected to have a 56-byte flag."
        )
    # With a 56-byte flag, the known suffix decrypts exactly the seven v coefficients
    # of the first RNG block. Then u is any monic degree-7 factor of f - v^2.
    v_bytes = bytes(c ^ m for c, m in zip(ct[HALF:BLOCK], SUFFIX))
    vcoef = list(struct.unpack("<7Q", v_bytes))
    v = vcoef
    h = poly_sub(f, poly_mul(v, v))
    candidates = []
    for u in factor_monic_degree7_divisors(h):
        if len(u) != 8 or u[-1] != 1:
            continue
        ucoef = u[:7]
        # The challenge rejected 0/1 coefficients before output; this removes noise.
        if any(c in (0, 1) for c in ucoef + vcoef):
            continue
        flag = bytes(c ^ k for c, k in zip(ct[:HALF], struct.pack("<7Q", *ucoef)))
        candidates.append((score_plaintext(flag), flag, ucoef))
    candidates.sort(reverse=True, key=lambda t: t[0])
    return candidates

# ---------- IO wrappers ----------
class RemoteIO:
    def __init__(self, host, port):
        self.sock = socket.create_connection((host, int(port)), timeout=20)
        self.f = self.sock.makefile("rwb", buffering=0)
    def readline(self):
        line = self.f.readline()
        if not line:
            raise EOFError("remote closed connection")
        return line
    def sendline(self, data):
        self.f.write(data + b"\n")
    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass

class LocalIO:
    def __init__(self, chall_path):
        fake_flag = b"crypto{" + b"L" * 48 + b"}"
        assert len(fake_flag) == 56
        env = os.environ.copy()
        env["FLAG"] = fake_flag.decode()
        self.expected = fake_flag
        try:
            self.p = subprocess.Popen(
                ["sage", chall_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
                env=env,
                bufsize=0,
            )
        except FileNotFoundError as e:
            raise RuntimeError("Sage is required for local mode because the challenge file is .sage; install Sage or run remote mode only") from e
    def readline(self):
        line = self.p.stdout.readline()
        if not line:
            err = self.p.stderr.read().decode(errors="replace")
            raise EOFError("local process closed" + (":\n" + err if err else ""))
        return line
    def sendline(self, data):
        self.p.stdin.write(data + b"\n")
        self.p.stdin.flush()
    def close(self):
        try:
            self.p.kill()
        except Exception:
            pass

def open_challenge(mode, args):
    if mode == "remote":
        if len(args) != 2:
            raise SystemExit("usage: python3 solve_what_curve.py remote HOST PORT")
        return RemoteIO(args[0], args[1])
    if mode == "local":
        if len(args) != 1:
            raise SystemExit("usage: python3 solve_what_curve.py local /path/to/chall.sage")
        return LocalIO(args[0])
    raise SystemExit("mode must be: selftest | local | remote")

def solve_session(io):
    ct_hex = io.readline().strip()
    try:
        ct = bytes.fromhex(ct_hex.decode())
    except Exception:
        raise ValueError(f"first line was not hex: {ct_hex!r}")
    prompt = io.readline()  # Enter your message :
    print(f"[+] flag ciphertext length: {len(ct)} bytes")

    io.sendline((b"\x00" * (3 * BLOCK)).hex().encode())
    raw_hex = io.readline().strip()
    raw = bytes.fromhex(raw_hex.decode())
    _ = io.readline()      # next prompt
    print(f"[+] collected {len(raw) // BLOCK} full oracle blocks")

    f = recover_curve_f(raw)
    print("[+] recovered hidden curve polynomial f")

    candidates = recover_flag_from_first_ciphertext(ct, f)
    if not candidates:
        raise RuntimeError("no flag candidate found")
    print(f"[+] {len(candidates)} candidate(s); best first")
    for score, flag, _ in candidates[:10]:
        print(f"score={score:4d}  {flag!r}")
    return candidates[0][1]

# ---------- self-test without Sage/network ----------
def legendre(a):
    return pow(a % p, (p - 1) // 2, p)

def sqrt_mod_p_3mod4(a):
    a %= p
    if a == 0:
        return 0
    if legendre(a) != 1:
        return None
    r = pow(a, (p + 1) // 4, p)
    return r if r * r % p == a else None

def interpolate(xs, ys):
    res = [0]
    for i, xi in enumerate(xs):
        num = [1]
        den = 1
        for j, xj in enumerate(xs):
            if i == j:
                continue
            num = poly_mul(num, [(-xj) % p, 1])
            den = den * ((xi - xj) % p) % p
        scale = ys[i] * pow(den, -1, p) % p
        res = poly_add(res, [(scale * c) % p for c in num])
    return res

def random_valid_divisor(f):
    xs, ys, seen = [], [], set()
    while len(xs) < 7:
        xx = random.randrange(2, p)
        if xx in seen:
            continue
        yy = sqrt_mod_p_3mod4(poly_eval(f, xx))
        if yy is None or yy in (0, 1):
            continue
        seen.add(xx)
        xs.append(xx)
        ys.append(min(yy, p - yy))
    u = [1]
    for xx in xs:
        u = poly_mul(u, [(-xx) % p, 1])
    v = interpolate(xs, ys) + [0] * 7
    v = v[:7]
    assert len(u) == 8 and poly_mod(poly_sub(f, poly_mul(v, v)), u) == [0]
    return u[:7], v

def selftest():
    random.seed(1337)
    f = [random.randrange(p) for _ in range(16)]
    f[15] = random.randrange(1, p)
    blocks = [random_valid_divisor(f) for _ in range(3)]
    raw = b"".join(struct.pack("<14Q", *(u + v)) for u, v in blocks)
    f2 = recover_curve_f(raw)
    assert f2 == f
    flag = b"crypto{" + b"A" * 48 + b"}"
    first = raw[:BLOCK]
    ct = bytes(a ^ b for a, b in zip(first, flag + SUFFIX))
    cands = recover_flag_from_first_ciphertext(ct, f2)
    assert cands and cands[0][1] == flag
    print("[+] selftest ok")
    print(cands[0][1].decode())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(
            "usage:\n"
            "  python3 solve_what_curve.py selftest\n"
            "  python3 solve_what_curve.py local /path/to/chall.sage\n"
            "  python3 solve_what_curve.py remote archive.cryptohack.org 39003"
        )
    mode = sys.argv[1]
    if mode == "selftest":
        selftest()
    else:
        io = open_challenge(mode, sys.argv[2:])
        try:
            flag = solve_session(io)
            if hasattr(io, "expected"):
                print(f"[+] local expected: {io.expected!r}")
                print("[+] local solve OK" if flag == io.expected else "[!] local solve mismatch")
        finally:
            io.close()
