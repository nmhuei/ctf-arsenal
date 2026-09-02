#!/usr/bin/env python3
"""
Solve Blind (ECSC 2023 Norway / CryptoHack static archive)

Usage:
  python3 solve_blind.py /path/to/output.txt

Dependencies for final decrypt:
  pip install bcrypt cryptography

The EC/signature search is pure Python and does not need Sage.
"""
import ast
import hashlib
import operator
import re
import sys
import time
import warnings
from pathlib import Path

# ---------- challenge constants ----------
FIELD = 2**448 - 2**224 - 1
ED_A = 1
ED_D = int(
    "fffffffffffffffffffffffffffffffffffffffffffffffffffffffe"
    "ffffffffffffffffffffffffffffffffffffffffffffffffffff6756", 16
) % FIELD
ORDER = int(
    "3fffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    "7cca23e9c44edb49aed63690216cc2728dc58f552378c292ab5844f3", 16
)
A = ((-pow(48, -1, FIELD)) * (ED_A * ED_A + 14 * ED_A * ED_D + ED_D * ED_D)) % FIELD
B = (pow(864, -1, FIELD) * (ED_A + ED_D) * (-(ED_A * ED_A) + 34 * ED_A * ED_D - ED_D * ED_D)) % FIELD

GX_TE = int(
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa955555555555555555555555555555555555555555555555555555555", 16
)
GY_TE = int(
    "ae05e9634ad7048db359d6205086c2b0036ed7a035884dd7b7e36d728ad8c4b80d6565833a2a3098bbbcb2bed1cda06bdaeafbcdea9386ed", 16
)

K2 = 128
K1 = 8 * ((7 + FIELD.bit_length()) // 8) - K2       # 320
KBITS = 8 * ((ORDER.bit_length() + 7) // 8)          # 448
MSG_BYTES = (K1 + K2) // 8                           # 56
O = (0, 1, 0)  # Jacobian infinity


def inv(x: int) -> int:
    return pow(x % FIELD, -1, FIELD)


def to_weierstrass(x: int, y: int):
    x %= FIELD
    y %= FIELD
    u = ((5 * ED_A + ED_A * y - 5 * ED_D * y - ED_D) * inv(12 - 12 * y)) % FIELD
    v = ((ED_A + ED_A * y - ED_D * y - ED_D) * inv(4 * x - 4 * x * y)) % FIELD
    return u, v


G_AFF = to_weierstrass(GX_TE, GY_TE)


def is_inf(P):
    return P[2] == 0


def affine_to_jac(P):
    if P is None:
        return O
    return P[0] % FIELD, P[1] % FIELD, 1


def jac_to_aff(P):
    X, Y, Z = P
    if Z == 0:
        return None
    zi = inv(Z)
    zi2 = (zi * zi) % FIELD
    return (X * zi2) % FIELD, (Y * zi2 * zi) % FIELD


def dbl(P):
    X1, Y1, Z1 = P
    if Z1 == 0 or Y1 == 0:
        return O
    XX = (X1 * X1) % FIELD
    YY = (Y1 * Y1) % FIELD
    YYYY = (YY * YY) % FIELD
    ZZ = (Z1 * Z1) % FIELD
    S = (4 * X1 * YY) % FIELD
    M = (3 * XX + A * ((ZZ * ZZ) % FIELD)) % FIELD
    T = (M * M - 2 * S) % FIELD
    X3 = T
    Y3 = (M * (S - T) - 8 * YYYY) % FIELD
    Z3 = (2 * Y1 * Z1) % FIELD
    return X3, Y3, Z3


def add_mixed(P, Q):
    if Q is None:
        return P
    if is_inf(P):
        return affine_to_jac(Q)
    X1, Y1, Z1 = P
    x2, y2 = Q
    Z1Z1 = (Z1 * Z1) % FIELD
    U2 = (x2 * Z1Z1) % FIELD
    S2 = (y2 * Z1 * Z1Z1) % FIELD
    H = (U2 - X1) % FIELD
    R = (S2 - Y1) % FIELD
    if H == 0:
        return dbl(P) if R == 0 else O
    HH = (H * H) % FIELD
    HHH = (HH * H) % FIELD
    V = (X1 * HH) % FIELD
    X3 = (R * R - HHH - 2 * V) % FIELD
    Y3 = (R * (V - X3) - Y1 * HHH) % FIELD
    Z3 = (Z1 * H) % FIELD
    return X3, Y3, Z3


def add_aff(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    return jac_to_aff(add_mixed(affine_to_jac(P), Q))


def precompute_pair(G, Y, w=5):
    """Precompute i*G + j*Y for Shamir fixed-window multiplication."""
    n = 1 << w
    gm = [None] * n
    ym = [None] * n
    gm[1] = G
    ym[1] = Y
    for i in range(2, n):
        gm[i] = add_aff(gm[i - 1], G)
        ym[i] = add_aff(ym[i - 1], Y)
    table = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == 0:
                table[i][j] = ym[j]
            elif j == 0:
                table[i][j] = gm[i]
            else:
                table[i][j] = add_aff(gm[i], ym[j])
    return table


def shamir(k_g, k_y, table, w=5):
    """Return k_g*G + k_y*Y using precomputed pair table."""
    k_g %= ORDER
    k_y %= ORDER
    windows = (ORDER.bit_length() + w - 1) // w
    mask = (1 << w) - 1
    R = O
    for pos in range(windows - 1, -1, -1):
        if not is_inf(R):
            for _ in range(w):
                R = dbl(R)
        i = (k_g >> (pos * w)) & mask
        j = (k_y >> (pos * w)) & mask
        if i or j:
            R = add_mixed(R, table[i][j])
    return jac_to_aff(R)


def Hash(x: bytes, nin: int, n: int, div: bytes) -> bytes:
    assert nin % 8 == n % 8 == 0
    nin //= 8
    n //= 8
    assert len(x) == nin
    out = b""
    ctr = 0
    while len(out) < n:
        out += hashlib.sha256(x + b"||" + div + ctr.to_bytes(8, "big")).digest()
        ctr += 1
    return out[:n]


def F1(x: bytes) -> bytes:
    return Hash(x, K2, K1, b"1")


def F2(x: bytes) -> bytes:
    return Hash(x, K1, K2, b"2")


def H(x: bytes) -> bytes:
    return Hash(x, K1 + K2, KBITS, b"H")


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(map(operator.xor, a, b))


def parse_output(path: Path):
    s = path.read_text()
    y_m = re.search(r"Y = \((\d+), (\d+)\)", s)
    ct_m = re.search(r"ct = ([0-9a-f]+)", s)
    if not y_m or not ct_m:
        raise ValueError("Could not parse Y/ct from output.txt")
    sigs = ast.literal_eval(s[s.index("["):])
    Y = to_weierstrass(int(y_m.group(1)), int(y_m.group(2)))
    ct = bytes.fromhex(ct_m.group(1))
    return Y, ct, sigs


def find_seed(output_path: Path):
    Y, ct, sigs = parse_output(output_path)
    print(f"[*] loaded {len(sigs)} signatures, ct={len(ct)} bytes")
    print("[*] precomputing EC table...")
    t0 = time.time()
    table = precompute_pair(G_AFF, Y, w=5)
    print(f"[*] table ready in {time.time() - t0:.2f}s")

    t0 = time.time()
    for idx, (r_hex, z) in enumerate(sigs):
        r = bytes.fromhex(r_hex)
        c = int.from_bytes(H(r), "big")
        R = shamir(z, c, table, w=5)  # zG + cY = omegaG for the real signature
        if R is None:
            continue
        m1 = xor(int(R[0]).to_bytes(MSG_BYTES, "big"), r)
        h_part = m1[: K1 // 8]
        seed = xor(F2(h_part), m1[K1 // 8 :])
        if F1(seed) == h_part:
            print(f"[+] valid signature index = {idx}")
            print(f"[+] recovered seed       = {seed.hex()}")
            return seed, ct
        if idx and idx % 1000 == 0:
            print(f"    checked {idx}/{len(sigs)} in {time.time() - t0:.1f}s")
    raise RuntimeError("valid signature not found")


def aes_ctr_decrypt(key: bytes, ct: bytes) -> bytes:
    try:
        from Crypto.Cipher import AES
        return AES.new(key, AES.MODE_CTR, nonce=b"").decrypt(ct)
    except Exception:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        return Cipher(algorithms.AES(key), modes.CTR(b"\x00" * 16)).decryptor().update(ct)


def derive_key(seed: bytes) -> bytes:
    import bcrypt
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return bcrypt.kdf(seed, b"ICC_CHALLENGE", 16, 31337)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} output.txt", file=sys.stderr)
        sys.exit(2)
    seed, ct = find_seed(Path(sys.argv[1]))
    print("[*] running bcrypt.kdf(seed, b'ICC_CHALLENGE', 16, 31337) ...")
    t0 = time.time()
    key = derive_key(seed)
    print(f"[+] AES key = {key.hex()}  ({time.time() - t0:.1f}s)")
    flag = aes_ctr_decrypt(key, ct)
    print(f"[+] flag = {flag.decode(errors='replace')}")


if __name__ == "__main__":
    main()
