#!/usr/bin/env python3
import json
import os
import socket
import sys
from itertools import product

# Pure-python exploit for CryptoHack "Ticket Maestro".
# It uses Groth16 proof re-randomization:
#   (A, B, C) -> (A, B + s*delta_g2, C + s*A)
# for the verifier's delta_g2.  The proof bytes change, so the server's
# Blake2 spent-id changes, but the proof remains valid.

FQ_MOD = 21888242871839275222246405745257275088696311157297823662689037894645226208583
FR_MOD = 21888242871839275222246405745257275088548364400416034343698204186575808495617
INV2 = (FQ_MOD + 1) // 2
# ark-bn254 G2 uses Fq2 = Fq[u]/(u^2 + 1) and b_twist = 3 / (9 + u)
B_TWIST = (
    (27 * pow(82, -1, FQ_MOD)) % FQ_MOD,
    (-3 * pow(82, -1, FQ_MOD)) % FQ_MOD,
)


def fq(x):
    return x % FQ_MOD


def fqi(x):
    return pow(x % FQ_MOD, -1, FQ_MOD)


def fq_sqrt(a):
    a %= FQ_MOD
    if a == 0:
        return 0
    # FQ_MOD == 3 mod 4
    y = pow(a, (FQ_MOD + 1) // 4, FQ_MOD)
    if (y * y - a) % FQ_MOD != 0:
        return None
    return y


def fq_is_square(a):
    a %= FQ_MOD
    return a == 0 or pow(a, (FQ_MOD - 1) // 2, FQ_MOD) == 1


def fq_neg(a):
    return (-a) % FQ_MOD


# ---- Fq2 helpers, represented as (c0, c1) for c0 + c1*u, u^2 = -1 ----

def f2(a, b=0):
    return (a % FQ_MOD, b % FQ_MOD)


def f2_add(x, y):
    return ((x[0] + y[0]) % FQ_MOD, (x[1] + y[1]) % FQ_MOD)


def f2_sub(x, y):
    return ((x[0] - y[0]) % FQ_MOD, (x[1] - y[1]) % FQ_MOD)


def f2_neg(x):
    return ((-x[0]) % FQ_MOD, (-x[1]) % FQ_MOD)


def f2_mul(x, y):
    a, b = x
    c, d = y
    return ((a * c - b * d) % FQ_MOD, (a * d + b * c) % FQ_MOD)


def f2_sqr(x):
    a, b = x
    return ((a * a - b * b) % FQ_MOD, (2 * a * b) % FQ_MOD)


def f2_inv(x):
    a, b = x
    den = (a * a + b * b) % FQ_MOD
    inv = pow(den, -1, FQ_MOD)
    return (a * inv % FQ_MOD, (-b) * inv % FQ_MOD)


def f2_div(x, y):
    return f2_mul(x, f2_inv(y))


def f2_scale(x, n):
    return (x[0] * n % FQ_MOD, x[1] * n % FQ_MOD)


def f2_eq(x, y):
    return x[0] % FQ_MOD == y[0] % FQ_MOD and x[1] % FQ_MOD == y[1] % FQ_MOD


def f2_sqrt(z):
    # sqrt(a + bu) over Fq, q == 3 mod 4, u^2 = -1
    a, b = z[0] % FQ_MOD, z[1] % FQ_MOD
    if a == 0 and b == 0:
        return (0, 0)
    if b == 0:
        r = fq_sqrt(a)
        if r is not None:
            return (r, 0)
        r = fq_sqrt((-a) % FQ_MOD)
        if r is not None:
            return (0, r)
        return None

    alpha = fq_sqrt((a * a + b * b) % FQ_MOD)
    if alpha is None:
        return None
    for sign in (1, -1):
        t = ((a + sign * alpha) * INV2) % FQ_MOD
        x0 = fq_sqrt(t)
        if x0 is not None and x0 != 0:
            y0 = b * pow((2 * x0) % FQ_MOD, -1, FQ_MOD) % FQ_MOD
            root = (x0, y0)
            if f2_eq(f2_sqr(root), z):
                return root
    return None


# ---- elliptic curve helpers ----
# G1: y^2 = x^3 + 3 over Fq
# G2: y^2 = x^3 + B_TWIST over Fq2

def g1_neg(P):
    if P is None:
        return None
    return (P[0], (-P[1]) % FQ_MOD)


def g1_add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % FQ_MOD == 0:
        return None
    if x1 == x2 and y1 == y2:
        if y1 == 0:
            return None
        lam = (3 * x1 * x1) * pow((2 * y1) % FQ_MOD, -1, FQ_MOD) % FQ_MOD
    else:
        lam = (y2 - y1) * pow((x2 - x1) % FQ_MOD, -1, FQ_MOD) % FQ_MOD
    x3 = (lam * lam - x1 - x2) % FQ_MOD
    y3 = (lam * (x1 - x3) - y1) % FQ_MOD
    return (x3, y3)


def g1_mul(P, n):
    n %= FR_MOD
    R = None
    Q = P
    while n:
        if n & 1:
            R = g1_add(R, Q)
        Q = g1_add(Q, Q)
        n >>= 1
    return R


def g2_neg(P):
    if P is None:
        return None
    return (P[0], f2_neg(P[1]))


def g2_add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if f2_eq(x1, x2) and f2_eq(f2_add(y1, y2), (0, 0)):
        return None
    if f2_eq(x1, x2) and f2_eq(y1, y2):
        if f2_eq(y1, (0, 0)):
            return None
        lam = f2_div(f2_scale(f2_sqr(x1), 3), f2_scale(y1, 2))
    else:
        lam = f2_div(f2_sub(y2, y1), f2_sub(x2, x1))
    x3 = f2_sub(f2_sub(f2_sqr(lam), x1), x2)
    y3 = f2_sub(f2_mul(lam, f2_sub(x1, x3)), y1)
    return (x3, y3)


def g2_mul(P, n):
    n %= FR_MOD
    R = None
    Q = P
    while n:
        if n & 1:
            R = g2_add(R, Q)
        Q = g2_add(Q, Q)
        n >>= 1
    return R


# ---- arkworks compressed serialization helpers ----
# Field elements are little-endian 32-byte integers.  The two high bits of the
# last byte encode SWFlags: 0x80 means one y root, 0x00 the opposite root,
# 0x40 is infinity.  To be robust across ark sign convention details, this
# exploit enumerates both roots and both output sign flags.

def le_int(bs):
    return int.from_bytes(bs, 'little')


def int_le(x):
    return (x % FQ_MOD).to_bytes(32, 'little')


def clear_flags_32(bs):
    b = bytearray(bs)
    flags = b[-1] & 0xC0
    b[-1] &= 0x3F
    return bytes(b), flags


def parse_g1_x(comp):
    raw, flags = clear_flags_32(comp)
    if flags == 0x40:
        return None, flags
    x = le_int(raw)
    return x, flags


def parse_g2_x(comp):
    c0raw = comp[:32]
    c1raw, flags = clear_flags_32(comp[32:64])
    if flags == 0x40:
        return None, flags
    return (le_int(c0raw), le_int(c1raw)), flags


def g1_roots_from_comp(comp):
    x, flags = parse_g1_x(comp)
    if x is None:
        return [None]
    rhs = (pow(x, 3, FQ_MOD) + 3) % FQ_MOD
    y = fq_sqrt(rhs)
    if y is None:
        raise ValueError('G1 x-coordinate is not on curve; check serialization assumptions')
    return [(x, y), (x, (-y) % FQ_MOD)] if y else [(x, 0)]


def g2_roots_from_comp(comp):
    x, flags = parse_g2_x(comp)
    if x is None:
        return [None]
    rhs = f2_add(f2_mul(f2_sqr(x), x), B_TWIST)
    y = f2_sqrt(rhs)
    if y is None:
        raise ValueError('G2 x-coordinate is not on twist; check serialization assumptions')
    neg = f2_neg(y)
    return [(x, y)] if f2_eq(y, neg) else [(x, y), (x, neg)]


def compress_g1_with_flag(P, pos_flag):
    if P is None:
        b = bytearray(32)
        b[-1] |= 0x40
        return bytes(b)
    x, _ = P
    b = bytearray(int_le(x))
    if pos_flag:
        b[-1] |= 0x80
    return bytes(b)


def compress_g2_with_flag(P, pos_flag):
    if P is None:
        b = bytearray(64)
        b[-1] |= 0x40
        return bytes(b)
    x, _ = P
    b = bytearray(int_le(x[0]) + int_le(x[1]))
    if pos_flag:
        b[-1] |= 0x80
    return bytes(b)


def split_proof(proof_hex):
    raw = bytes.fromhex(proof_hex)
    if len(raw) != 128:
        raise ValueError(f'Expected compressed proof length 128 bytes, got {len(raw)} bytes')
    return raw[:32], raw[32:96], raw[96:128]


def extract_delta_g2(vk_hex):
    raw = bytes.fromhex(vk_hex)
    # compressed VerifyingKey layout in ark-groth16 0.3:
    # alpha_g1(32), beta_g2(64), gamma_g2(64), delta_g2(64), gamma_abc_g1 Vec...
    if len(raw) < 224:
        raise ValueError(f'Verifying key too short: {len(raw)} bytes')
    return raw[32 + 64 + 64: 32 + 64 + 64 + 64]


def make_mutated_proof(a_seg_original, A, B, C, delta, csign, s, out_b_flag, out_c_flag):
    B2 = g2_add(B, g2_mul(delta, s))
    C2 = g1_add(C, g1_mul(A, (csign * s) % FR_MOD))
    return (a_seg_original + compress_g2_with_flag(B2, out_b_flag) + compress_g1_with_flag(C2, out_c_flag)).hex()


class Remote:
    def __init__(self, host, port):
        self.s = socket.create_connection((host, int(port)), timeout=10)
        self.f = self.s.makefile('rwb', buffering=0)
        hello = self.readline_json()
        print('[+] hello:', hello)

    def close(self):
        self.s.close()

    def readline_json(self):
        line = self.f.readline()
        if not line:
            raise EOFError('server closed connection')
        return json.loads(line.decode())

    def request(self, obj):
        self.f.write(json.dumps(obj).encode() + b'\n')
        return self.readline_json()

    def balance(self):
        r = self.request('Balance')
        return r.get('Balance')

    def buy_ticket(self):
        r = self.request('BuyTicket')
        if 'Ticket' not in r:
            raise RuntimeError(f'BuyTicket failed: {r}')
        return r['Ticket']['proof']

    def vk(self):
        r = self.request('VerifyingKey')
        return r['VerifyingKey']

    def redeem(self, proof_hex):
        return self.request({'Redeem': {'proof': proof_hex}})

    def buy_flag(self):
        return self.request('BuyFlag')


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else 'archive.cryptohack.org'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 26896
    rem = Remote(host, port)
    try:
        print('[+] initial balance:', rem.balance())
        vk_hex = rem.vk()
        delta_seg = extract_delta_g2(vk_hex)
        delta_roots = g2_roots_from_comp(delta_seg)
        print('[+] got verifying key; delta roots:', len(delta_roots))

        base_proof = rem.buy_ticket()
        print('[+] bought one ticket; balance:', rem.balance())
        a_seg, b_seg, c_seg = split_proof(base_proof)
        A_roots = g1_roots_from_comp(a_seg)
        B_roots = g2_roots_from_comp(b_seg)
        C_roots = g1_roots_from_comp(c_seg)
        print(f'[+] proof roots: A={len(A_roots)} B={len(B_roots)} C={len(C_roots)}')

        # Redeem the original ticket once; the mutations have different proof bytes.
        print('[+] redeem original:', rem.redeem(base_proof), 'balance:', rem.balance())

        # First successful mutated proof discovers all sign/convention choices.
        found = None
        attempts = 0
        for A, B, C, delta, csign in product(A_roots, B_roots, C_roots, delta_roots, (1, -1)):
            if found is not None:
                break
            for bf, cf in product((False, True), repeat=2):
                attempts += 1
                proof = make_mutated_proof(a_seg, A, B, C, delta, csign, 1, bf, cf)
                resp = rem.redeem(proof)
                if 'GoodTicket' in resp:
                    found = (A, B, C, delta, csign, bf, cf)
                    print(f'[+] found valid rerandomization after {attempts} attempts; balance:', rem.balance())
                    break
        if found is None:
            raise RuntimeError('Could not find a valid rerandomized proof. Serialization assumptions may differ.')

        A, B, C, delta, csign, _, _ = found
        s = 2
        while rem.balance() < 20:
            ok = False
            for bf, cf in product((False, True), repeat=2):
                proof = make_mutated_proof(a_seg, A, B, C, delta, csign, s, bf, cf)
                resp = rem.redeem(proof)
                if 'GoodTicket' in resp:
                    print(f'[+] redeemed mutation s={s}; balance:', rem.balance())
                    ok = True
                    break
            if not ok:
                print(f'[!] no output flags worked for s={s}; continuing')
            s += 1
            if s > 200:
                raise RuntimeError('too many attempts')

        print('[+] buy flag:')
        print(rem.buy_flag())
    finally:
        rem.close()


if __name__ == '__main__':
    main()
