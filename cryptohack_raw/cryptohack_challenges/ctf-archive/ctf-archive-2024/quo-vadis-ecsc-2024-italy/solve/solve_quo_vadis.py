#!/usr/bin/env python3
import ast
import hashlib
import random
import re
import socket
import sys
from dataclasses import dataclass
from typing import List, Tuple

# ---------------- GF(2^n), represented as bits mod the R2 defining polynomial ----------------

class GF2N:
    def __init__(self, n: int, mod_poly_bits: int):
        self.n = n
        self.mod = mod_poly_bits          # includes x^n bit
        self.red = mod_poly_bits ^ (1 << n)
        self.mask = (1 << n) - 1

    def add(self, a, b): return a ^ b

    def mul(self, a: int, b: int) -> int:
        res = 0
        aa = a
        bb = b
        while bb:
            if bb & 1:
                res ^= aa
            bb >>= 1
            aa <<= 1
            if aa & (1 << self.n):
                aa ^= self.mod
        return res & self.mask

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError("GF inverse of 0")
        return self.pow(a, (1 << self.n) - 2)

    def rand(self) -> int:
        return random.randrange(1 << self.n)

# ---------------- Polynomials over GF(2^n) ----------------

def _trim(p):
    p = p[:]
    while p and p[-1] == 0:
        p.pop()
    return p

def pdeg(p): return len(_trim(p)) - 1

def padd(a, b, F: GF2N):
    n = max(len(a), len(b))
    c = [0] * n
    for i in range(n):
        c[i] = (a[i] if i < len(a) else 0) ^ (b[i] if i < len(b) else 0)
    return _trim(c)

def pmul(a, b, F: GF2N):
    if not a or not b:
        return []
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    c[i+j] ^= F.mul(x, y)
    return _trim(c)

def pdivmod(a, b, F: GF2N):
    a = _trim(a)
    b = _trim(b)
    if not b:
        raise ZeroDivisionError("poly div by 0")
    db = len(b) - 1
    inv_lc = F.inv(b[-1])
    q = [0] * max(1, (len(a) - len(b) + 1))
    while len(a) >= len(b) and a:
        d = len(a) - len(b)
        coef = F.mul(a[-1], inv_lc)
        q[d] = coef
        if coef:
            for i in range(db + 1):
                a[d+i] ^= F.mul(coef, b[i])
        a = _trim(a)
    return _trim(q), a

def pmod(a, m, F: GF2N):
    return pdivmod(a, m, F)[1]

def pgcd(a, b, F: GF2N):
    a = _trim(a); b = _trim(b)
    while b:
        _, r = pdivmod(a, b, F)
        a, b = b, r
    if not a:
        return []
    inv = F.inv(a[-1])
    return [F.mul(x, inv) for x in a]

def psquare_mod(a, m, F: GF2N):
    return pmod(pmul(a, a, F), m, F)

def linear_factors_split(f, F: GF2N):
    """Return monic linear factors of a split squarefree polynomial over GF(2^n)."""
    f = _trim(f)
    d = pdeg(f)
    if d <= 0:
        return []
    # monic
    if f[-1] != 1:
        inv = F.inv(f[-1])
        f = [F.mul(x, inv) for x in f]
    if d == 1:
        return [f]

    # Cantor-Zassenhaus special case for linear factors in characteristic 2:
    # split by Trace_{GF(2^n)/GF(2)}(h) mod f.
    for _ in range(200):
        h = [F.rand() for _ in range(d)]
        h = _trim(h)
        if pdeg(h) <= 0:
            continue
        t = []
        u = pmod(h, f, F)
        for _i in range(F.n):
            t = padd(t, u, F)
            u = psquare_mod(u, f, F)
        g = pgcd(t, f, F)
        dg = pdeg(g)
        if 0 < dg < d:
            q, r = pdivmod(f, g, F)
            assert not r
            return linear_factors_split(g, F) + linear_factors_split(q, F)
    raise RuntimeError("failed to split polynomial; try again")

def roots_of_split_poly(coeffs, F: GF2N):
    roots = []
    for fac in linear_factors_split(coeffs, F):
        # fac = c0 + c1*x, root = c0/c1 in characteristic 2
        roots.append(F.mul(fac[0], F.inv(fac[1])))
    return roots

# ---------------- Galois ring R2 = (Z/2^k Z)[x]/(M) ----------------

class GRElem:
    __slots__ = ("ring", "c")
    def __init__(self, ring, coeffs):
        self.ring = ring
        n = ring.n
        mask = ring.mask
        cc = list(coeffs)[:n] + [0] * max(0, n - len(coeffs))
        self.c = [x & mask for x in cc[:n]]

    def __add__(self, other):
        other = self.ring.coerce(other)
        return GRElem(self.ring, [(a + b) & self.ring.mask for a, b in zip(self.c, other.c)])
    __radd__ = __add__

    def __sub__(self, other):
        other = self.ring.coerce(other)
        return GRElem(self.ring, [(a - b) & self.ring.mask for a, b in zip(self.c, other.c)])

    def __rsub__(self, other):
        return self.ring.coerce(other).__sub__(self)

    def __neg__(self):
        return GRElem(self.ring, [(-a) & self.ring.mask for a in self.c])

    def __mul__(self, other):
        other = self.ring.coerce(other)
        return self.ring.mul(self, other)
    __rmul__ = __mul__

    def __pow__(self, e: int):
        if e < 0:
            return self.inv().__pow__(-e)
        r = self.ring.one()
        a = self
        while e:
            if e & 1:
                r = r * a
            a = a * a
            e >>= 1
        return r

    def __eq__(self, other):
        other = self.ring.coerce(other)
        return self.c == other.c

    def is_zero(self):
        return all(x == 0 for x in self.c)

    def mod2_bits(self):
        z = 0
        for i, x in enumerate(self.c):
            if x & 1:
                z |= 1 << i
        return z

    def inv(self):
        F = self.ring.gf
        a0 = self.mod2_bits()
        b0 = F.inv(a0)
        b = self.ring.from_bits(b0)
        two = self.ring.scalar(2)
        # doubles 2-adic precision each step
        for _ in range(self.ring.k.bit_length() + 2):
            b = b * (two - self * b)
        return b

    def __repr__(self):
        return f"GRElem({self.c})"

class GRing:
    def __init__(self, k: int, mod_coeffs_low: List[int]):
        self.k = k
        self.q = 1 << k
        self.mask = self.q - 1
        self.mod_coeffs = [x & self.mask for x in mod_coeffs_low]  # M=x^n+sum m_i x^i
        self.n = len(mod_coeffs_low)
        bits = (1 << self.n)
        for i, x in enumerate(mod_coeffs_low):
            if x & 1:
                bits |= 1 << i
        self.gf = GF2N(self.n, bits)

    def elem(self, coeffs): return GRElem(self, coeffs)
    def zero(self): return GRElem(self, [])
    def one(self): return GRElem(self, [1])
    def scalar(self, x: int): return GRElem(self, [x])
    def gen(self): return GRElem(self, [0, 1])
    def from_bits(self, bits: int):
        return GRElem(self, [(bits >> i) & 1 for i in range(self.n)])
    def coerce(self, x):
        if isinstance(x, GRElem):
            if x.ring is not self:
                raise TypeError("wrong GRing")
            return x
        return self.scalar(int(x))

    def mul(self, A: GREElem if False else GRElem, B: GREElem if False else GRElem):
        n = self.n
        mask = self.mask
        tmp = [0] * (2*n - 1)
        for i, a in enumerate(A.c):
            if a:
                for j, b in enumerate(B.c):
                    if b:
                        tmp[i+j] += a*b
        for j in range(2*n - 2, n - 1, -1):
            c = tmp[j]
            if c:
                shift = j - n
                # x^n = -sum mod_coeffs[i] x^i
                for i, mi in enumerate(self.mod_coeffs):
                    if mi:
                        tmp[shift+i] -= c * mi
        return GRElem(self, [x & mask for x in tmp[:n]])

# ---------------- Small polynomial class used by eval() parser ----------------

class ParsedPoly:
    def __init__(self, coeffs, zero, one, mul_func=None):
        self.coeffs = coeffs[:]   # low to high, coefficients in GF int or GRElem
        self.zero = zero
        self.one = one
        self.mul_func = mul_func
        self._trim()
    def _is_zero_coeff(self, x):
        return x == self.zero
    def _trim(self):
        while self.coeffs and self._is_zero_coeff(self.coeffs[-1]):
            self.coeffs.pop()
    @classmethod
    def const(cls, c, zero, one, mul_func=None):
        return cls([] if c == zero else [c], zero, one, mul_func)
    @classmethod
    def var(cls, zero, one, mul_func=None):
        return cls([zero, one], zero, one, mul_func)
    def _coerce(self, other):
        if isinstance(other, ParsedPoly):
            return other
        if isinstance(self.zero, int):
            c = other & ((1 << 1000) - 1) if False else int(other)
            # for GF parser, int constants are just 0/1
            c &= 1
        else:
            c = self.zero.ring.scalar(int(other))
        return ParsedPoly.const(c, self.zero, self.one, self.mul_func)
    def __add__(self, other):
        other = self._coerce(other)
        n = max(len(self.coeffs), len(other.coeffs))
        out = []
        for i in range(n):
            a = self.coeffs[i] if i < len(self.coeffs) else self.zero
            b = other.coeffs[i] if i < len(other.coeffs) else self.zero
            out.append(a ^ b if isinstance(self.zero, int) else a + b)
        return ParsedPoly(out, self.zero, self.one, self.mul_func)
    __radd__ = __add__
    def __sub__(self, other):
        # In GR this is true subtraction; Sage printed m over char 2 has no minus,
        # but Python may call it for parsed constants. Keep it correct.
        other = self._coerce(other)
        n = max(len(self.coeffs), len(other.coeffs))
        out = []
        for i in range(n):
            a = self.coeffs[i] if i < len(self.coeffs) else self.zero
            b = other.coeffs[i] if i < len(other.coeffs) else self.zero
            out.append(a ^ b if isinstance(self.zero, int) else a - b)
        return ParsedPoly(out, self.zero, self.one, self.mul_func)
    def __rsub__(self, other): return self._coerce(other).__sub__(self)
    def __mul__(self, other):
        other = self._coerce(other)
        if not self.coeffs or not other.coeffs:
            return ParsedPoly([], self.zero, self.one, self.mul_func)
        out = [self.zero for _ in range(len(self.coeffs) + len(other.coeffs) - 1)]
        for i, a in enumerate(self.coeffs):
            for j, b in enumerate(other.coeffs):
                prod = (self.mul_func(a, b) if self.mul_func is not None else (a & b)) if isinstance(self.zero, int) else a * b
                out[i+j] = (out[i+j] ^ prod) if isinstance(self.zero, int) else out[i+j] + prod
        return ParsedPoly(out, self.zero, self.one, self.mul_func)
    __rmul__ = __mul__
    def __pow__(self, e: int):
        e = int(e)
        r = ParsedPoly.const(self.one, self.zero, self.one, self.mul_func)
        a = self
        while e:
            if e & 1:
                r = r * a
            a = a * a
            e >>= 1
        return r
    def __neg__(self):
        if isinstance(self.zero, int):
            return self
        return ParsedPoly([-c for c in self.coeffs], self.zero, self.one, self.mul_func)
    def __repr__(self): return f"ParsedPoly({self.coeffs})"

_var_re = re.compile(r"b\d+(?:bar)?")

def normalize_expr(s: str) -> str:
    s = s.strip()
    s = s.replace('^', '**')
    # Sage quotient variables may be b0bar, b1bar, ...; keep as identifiers but also map them.
    return s

def eval_poly_expr(expr: str, cur_idx: int, prev_consts, mode: str, ring: GRing = None):
    """Evaluate Sage polynomial expression as a polynomial in b_cur_idx.
    mode='gf': previous constants are GF2N ints, coefficients returned as ints.
    mode='gr': previous constants are GREElem, coefficients returned as GREElem.
    """
    expr = normalize_expr(expr)
    if mode == 'gf':
        zero, one = 0, 1
        mul_func = ring.gf.mul if ring is not None else None
    else:
        zero, one = ring.zero(), ring.one()
        mul_func = None
    env = {}
    # variables seen in expression plus a few likely names
    maxidx = cur_idx
    for v in _var_re.findall(expr):
        idx = int(re.search(r"\d+", v).group())
        maxidx = max(maxidx, idx)
    for i in range(maxidx + 1):
        if i == cur_idx:
            val = ParsedPoly.var(zero, one, mul_func)
        elif i < len(prev_consts):
            val = ParsedPoly.const(prev_consts[i], zero, one, mul_func)
        else:
            # Unknown future variable: should not happen.
            val = ParsedPoly.var(zero, one, mul_func)
        env[f"b{i}"] = val
        env[f"b{i}bar"] = val
    env['Integer'] = int
    poly = eval(expr, {"__builtins__": {}}, env)
    if not isinstance(poly, ParsedPoly):
        poly = ParsedPoly.const((poly & 1) if mode == 'gf' else ring.scalar(int(poly)), zero, one, mul_func)
    # Fill missing degrees up to current degree if needed outside.
    return poly.coeffs

# ---------------- Linear algebra modulo 2^k ----------------

def invert_matrix_mod_power2(A: List[List[int]], k: int) -> List[List[int]]:
    n = len(A)
    mod = 1 << k
    mask = mod - 1
    M = [[x & mask for x in row] + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(A)]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if M[r][col] & 1:
                piv = r
                break
        if piv is None:
            raise RuntimeError(f"matrix not invertible modulo 2 at column {col}")
        if piv != col:
            M[col], M[piv] = M[piv], M[col]
        invp = pow(M[col][col] & mask, -1, mod)
        M[col] = [(x * invp) & mask for x in M[col]]
        for r in range(n):
            if r == col:
                continue
            fac = M[r][col] & mask
            if fac:
                M[r] = [(M[r][c] - fac * M[col][c]) & mask for c in range(2*n)]
    return [row[n:] for row in M]

def mat_vec_mul(M: List[List[int]], v: List[int], k: int) -> List[int]:
    mask = (1 << k) - 1
    return [sum((a * b for a, b in zip(row, v)), 0) & mask for row in M]

# ---------------- Solver core ----------------

def parse_monic_gf2_poly(expr: str, n: int) -> List[int]:
    coeffs = eval_poly_expr(expr, 0, [], 'gf')
    coeffs += [0] * (n + 1 - len(coeffs))
    if len(coeffs) <= n or coeffs[n] != 1:
        raise ValueError(f"bad R2 polynomial degree {n}: {expr} -> {coeffs}")
    return [c & 1 for c in coeffs[:n]]

def poly_eval_gr(coeffs: List[GRElem], x: GRElem) -> GRElem:
    if not coeffs:
        return x.ring.zero()
    r = coeffs[-1]
    for c in reversed(coeffs[:-1]):
        r = r * x + c
    return r

def lift_root(poly_coeffs_gr: List[GRElem], root_bits: int, ring: GRing) -> GRElem:
    r = ring.from_bits(root_bits)
    deriv = []
    for i in range(1, len(poly_coeffs_gr)):
        deriv.append(poly_coeffs_gr[i] * i)
    if not deriv:
        raise RuntimeError("constant polynomial")
    for _ in range(ring.k.bit_length() + 3):
        val = poly_eval_gr(poly_coeffs_gr, r)
        if val.is_zero():
            break
        der = poly_eval_gr(deriv, r)
        r = r - val * der.inv()
    if not poly_eval_gr(poly_coeffs_gr, r).is_zero():
        raise RuntimeError("Hensel lift did not converge")
    return r

def basis_images(ds: List[int], roots: List[GRElem], ring: GRing) -> List[GRElem]:
    powtab = []
    for d, r in zip(ds, roots):
        arr = [ring.one()]
        for _ in range(1, d):
            arr.append(arr[-1] * r)
        powtab.append(arr)
    N = 1
    for d in ds:
        N *= d
    imgs = []
    for idx in range(N):
        t = idx
        e = ring.one()
        for i, d in enumerate(ds):
            ei = t % d
            t //= d
            e = e * powtab[i][ei]
        imgs.append(e)
    return imgs

def map_flat_to_r2(flat: List[int], imgs: List[GRElem], ring: GRing) -> GRElem:
    s = ring.zero()
    for c, b in zip(flat, imgs):
        if c:
            s = s + b * c
    return s

def prepare_challenge(k: int, ds: List[int], setup_lines: List[str]):
    """Given R1 polynomial lines, R2 polynomial line, pt1 line: return send vector and inverse map."""
    t = len(ds)
    if len(setup_lines) < t + 2:
        raise ValueError(f"not enough setup lines: {setup_lines}")
    r1_polys = [x.strip() for x in setup_lines[:t]]
    r2_poly = setup_lines[t].strip()
    pt1_line = setup_lines[t+1].strip()
    N = 1
    for d in ds: N *= d
    mod_coeffs = parse_monic_gf2_poly(r2_poly, N)
    ring = GRing(k, mod_coeffs)

    roots_gf = []
    roots_gr = []
    for i, (d, expr) in enumerate(zip(ds, r1_polys)):
        coeffs_gf = eval_poly_expr(expr, i, roots_gf, 'gf', ring)
        coeffs_gf += [0] * (d + 1 - len(coeffs_gf))
        # polynomial should be monic of degree d
        if len(coeffs_gf) <= d or coeffs_gf[d] != 1:
            raise RuntimeError(f"bad tower poly {expr}: {coeffs_gf}")
        root_options = roots_of_split_poly(coeffs_gf[:d+1], ring.gf)
        if not root_options:
            raise RuntimeError("no root found")
        rb = root_options[0]
        # Lift this same polynomial, but coefficients are previous GR roots.
        coeffs_gr = eval_poly_expr(expr, i, roots_gr, 'gr', ring)
        coeffs_gr += [ring.zero()] * (d + 1 - len(coeffs_gr))
        rg = lift_root(coeffs_gr[:d+1], rb, ring)
        roots_gf.append(rb)
        roots_gr.append(rg)

    imgs = basis_images(ds, roots_gr, ring)
    B = [[imgs[col].c[row] for col in range(N)] for row in range(N)]
    invB = invert_matrix_mod_power2(B, k)

    flat = [int(x) for x in pt1_line.split(',') if x.strip() != '']
    if len(flat) != N:
        raise RuntimeError(f"pt1 length {len(flat)} != {N}")
    pt2 = map_flat_to_r2(flat, imgs, ring)
    return pt2.c, invB, ring

def parse_nonempty_lines(blob: bytes) -> List[str]:
    text = blob.decode(errors='replace')
    text = text.replace('> ', '')
    return [ln.strip() for ln in text.splitlines() if ln.strip()]

def recv_until(sock, marker: bytes) -> bytes:
    data = b''
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    # keep simple; challenge output has no extra data after prompt in same packet that matters
    return data

def decrypt_flag(K: List[int], final_line: str) -> bytes:
    iv_hex, ct_hex = final_line.strip().split()
    key = hashlib.sha256("||".join(map(str, K)).encode()).digest()
    iv = bytes.fromhex(iv_hex); ct = bytes.fromhex(ct_hex)
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad
        return unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), 16)
    except Exception:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
        pt = dec.update(ct) + dec.finalize()
        pad = pt[-1]
        return pt[:-pad]

def solve_remote(host: str, port: int):
    params = [(2, [2,3]), (8, [2,3]), (8, [2,3,5]), (32, [3,4,5]), (64, [4,3,5])]
    K = []
    pending = None
    with socket.create_connection((host, port), timeout=30) as s:
        s.settimeout(650)
        block = recv_until(s, b'> ')
        lines = parse_nonempty_lines(block)
        for idx, (k, ds) in enumerate(params):
            if idx > 0:
                y_line = lines[0]
                y = [int(x) for x in y_line.split(',') if x.strip()]
                invB, prevk = pending
                K.extend(mat_vec_mul(invB, y, prevk))
                lines = lines[1:]
            send_vec, invB, ring = prepare_challenge(k, ds, lines)
            s.sendall((",".join(map(str, send_vec)) + "\n").encode())
            pending = (invB, k)
            if idx < len(params) - 1:
                block = recv_until(s, b'> ')
                lines = parse_nonempty_lines(block)
            else:
                tail = b''
                while True:
                    try:
                        chunk = s.recv(4096)
                    except socket.timeout:
                        break
                    if not chunk:
                        break
                    tail += chunk
                lines = parse_nonempty_lines(tail)
                y_line = lines[0]
                y = [int(x) for x in y_line.split(',') if x.strip()]
                invB, prevk = pending
                K.extend(mat_vec_mul(invB, y, prevk))
                final = lines[1]
                print(decrypt_flag(K, final).decode(errors='replace'))

if __name__ == '__main__':
    if len(sys.argv) == 3:
        solve_remote(sys.argv[1], int(sys.argv[2]))
    else:
        print(f"Usage: {sys.argv[0]} archive.cryptohack.org 23128")
