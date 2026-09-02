"""
PARITY REGISTRY :: gerege authority seal (scheme reference)

A gerege is the tablet of authority the Registry issues to those who move on the
Commons. Rather than hand its signature across the wire, a bearer proves, in
zero knowledge, that their tablet carries the Khan's authority: a Chaum-Pedersen
proof that one secret x ties the tablet point T = x*G to the authority binding
Y = x*K, where G and K are the two published generators.

The proof is made non-interactive with Fiat-Shamir. The verifier recomputes the
seal challenge from the *seal context* and checks the two Schnorr relations.

Curve: brainpoolP256r1. Points are serialised uncompressed: 0x04 || X || Y, each
coordinate 32 bytes big-endian. All scalars are reduced mod the group order n.

This module is the ground truth for both the gate and the handout. It holds no
secret: the authority scalar behind the Khan tablet is derived from a seed that
never leaves the Registry, and only the tablet points are published.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from ecdsa.curves import BRAINPOOLP256r1 as _CURVE
from ecdsa.ellipticcurve import Point

# --------------------------------------------------------------------- curve
G = _CURVE.generator
N = _CURVE.order
_C = _CURVE.curve
_P = _C.p()

DOMAIN = b"HZ-GEREGE-seal-v1\x00"
AUTHORITY_LABEL = b"HZ-GEREGE-authority-generator-v1"

INF = G * 0  # identity element of the group


def _hash_to_curve(label: bytes) -> Point:
    """Nothing-up-my-sleeve generator by try-and-increment. Discrete log unknown."""
    counter = 0
    while True:
        x = int.from_bytes(
            hashlib.sha256(label + counter.to_bytes(4, "big")).digest(), "big"
        ) % _P
        rhs = (x * x * x + _C.a() * x + _C.b()) % _P
        y = pow(rhs, (_P + 1) // 4, _P)  # p = 3 mod 4 on brainpoolP256r1
        if (y * y - rhs) % _P == 0:
            if y % 2:  # canonical: even y
                y = _P - y
            return Point(_C, x, y, N)
        counter += 1


# The authority generator K. Published; discrete log with respect to G unknown.
K = _hash_to_curve(AUTHORITY_LABEL)


# --------------------------------------------------------------------- codec
def enc_point(pt: Point) -> bytes:
    if pt == INF:
        raise ValueError("cannot encode the point at infinity")
    return b"\x04" + pt.x().to_bytes(32, "big") + pt.y().to_bytes(32, "big")


def dec_point(raw: bytes) -> Point:
    if len(raw) != 65 or raw[0] != 0x04:
        raise ValueError("expected an uncompressed point: 0x04 || X || Y")
    x = int.from_bytes(raw[1:33], "big")
    y = int.from_bytes(raw[33:65], "big")
    if x >= _P or y >= _P:
        raise ValueError("coordinate out of field range")
    if (y * y - (x * x * x + _C.a() * x + _C.b())) % _P != 0:
        raise ValueError("point is not on brainpoolP256r1")
    pt = Point(_C, x, y, N)
    if N * pt != INF:
        raise ValueError("point is not in the prime-order subgroup")
    return pt


def enc_hex(pt: Point) -> str:
    return enc_point(pt).hex()


def dec_hex(s: str) -> Point:
    return dec_point(bytes.fromhex(s.strip()))


# ------------------------------------------------------------------ challenge
def seal_challenge(session: bytes, T: Point, Y: Point) -> int:
    """
    The Fiat-Shamir seal challenge.

        c = SHA256( DOMAIN || session || enc(T) || enc(Y) ) mod n

    The seal context binds the session and the tablet pairing (T, Y). That is
    what the Registry decided a gerege must commit to.
    """
    pre = DOMAIN + session + enc_point(T) + enc_point(Y)
    return int.from_bytes(hashlib.sha256(pre).digest(), "big") % N


# -------------------------------------------------------------------- verify
@dataclass
class Attestation:
    T: Point
    Y: Point
    A: Point
    B: Point
    z: int


def verify(session: bytes, att: Attestation) -> bool:
    """
    A gerege attestation holds iff the two Chaum-Pedersen relations close under
    the seal challenge:

        z*G == A + c*T
        z*K == B + c*Y      with   c = seal_challenge(session, T, Y)
    """
    if not (0 <= att.z < N):
        return False
    c = seal_challenge(session, att.T, att.Y)
    ok1 = (att.z * G) == (att.A + c * att.T)
    ok2 = (att.z * K) == (att.B + c * att.Y)
    return ok1 and ok2


# ------------------------------------------------------- honest prover (demo)
def prove(session: bytes, x: int, rng) -> Attestation:
    """
    Honest prover for a tablet whose secret x is known (an envoy proving its own
    tablet). Used by the Registry only to mint the public demonstration seal.
    """
    x %= N
    T, Y = x * G, x * K
    r = rng(N)
    A, B = r * G, r * K
    c = seal_challenge(session, T, Y)
    z = (r + c * x) % N
    return Attestation(T=T, Y=Y, A=A, B=B, z=z)
