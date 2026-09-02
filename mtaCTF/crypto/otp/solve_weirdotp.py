#!/usr/bin/env python3
"""
Local solver / proof-of-concept for chall.py.

No networking is performed.

Use the functions with a captured transcript from the challenge service:
    n, d = recover_parameters(first_23_ciphertexts)
    seed = forge_seed(n)
    # submit this seed and an EMPTY plaintext hex string
    secret = recover_secret(encrypted_secret_hex, d)
    flag = decrypt_flag(encrypted_flag_hex, secret)

Run with --self-test to verify the full exploit against a local equivalent
implementation using flag{fake_flag}.
"""

import argparse
import hashlib
import math
import os
import random
import re
import socket
import sys
from typing import List, Sequence, Tuple

sys.set_int_max_str_digits(0)

MASK32 = 0xFFFFFFFF
N = 624
M = 397
MATRIX_A = 0x9908B0DF
UPPER_MASK = 0x80000000
LOWER_MASK = 0x7FFFFFFF

MSGS = [
    b"!@#$%^tung tung tung sahur!@#$%^",
    b"!@#$%^&tralalero tralala!@#$%^&*",
    b"!@#$%^bombardino crocodilo!@#$%^",
    b"!@#$%^&*(lirili larila!@#$%^&*()",
    b"!@#$%^&brr brr patapim!@#$%^&*!!",
    b"!@#$%^chimpanzini bananini!@#$%^",
    b"!@#$%^capuccino assassino!@#$%^&",
    b"!@#$%^ballerina cappuccina!@#$%@",
    b"!@#$%^&*()frigo camelo!@#$%^&*()",
    b"!@#$%^orangutini ananasini!@#$%^",
    b"!@#$%^&bombombini gusini!@#$%^&@",
    b"!@#$%^&*bobrito bandito!@#$%^&*@",
]


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def build_public_equations(ciphertexts: Sequence[str]) -> Tuple[List[List[int]], List[int], List[bytes]]:
    """Recover each 32-byte OTP state and its known coefficient row."""
    if len(ciphertexts) != 23:
        raise ValueError(f"need exactly 23 first-phase ciphertexts, got {len(ciphertexts)}")

    rng = random.Random(1337)
    rows: List[List[int]] = []
    states: List[int] = []
    plaintexts: List[bytes] = []

    for j, ct_hex in enumerate(ciphertexts):
        ct = bytes.fromhex(ct_hex.strip())
        if len(ct) != 32:
            raise ValueError(f"ciphertext #{j} must be 32 bytes, got {len(ct)}")

        pt = rng.choice(MSGS)
        coeff = [rng.getrandbits(256) + i for i in range(20)]
        ks = xor_bytes(ct, pt)
        state = int.from_bytes(ks, "big")

        rows.append(coeff + [1])  # unknown vector = a[0..19] || d
        states.append(state)
        plaintexts.append(pt)

    return rows, states, plaintexts


def _primitive_integer_null_vectors(rows: Sequence[Sequence[int]]) -> List[List[int]]:
    """Integer basis for left-nullspace of a 23x21 integer matrix."""
    from sympy import Matrix, ilcm

    ns = Matrix(rows).T.nullspace()
    if len(ns) != 2:
        raise RuntimeError(f"expected left-nullity 2, got {len(ns)}")

    out: List[List[int]] = []
    for v in ns:
        den = 1
        for x in v:
            den = int(ilcm(den, int(x.q)))
        z = [int(x * den) for x in v]
        g = 0
        for x in z:
            g = math.gcd(g, abs(x))
        if g:
            z = [x // g for x in z]
        out.append(z)
    return out


def _extract_256bit_prime_modulus(g: int, states: Sequence[int]) -> int:
    """G is n times a usually tiny accidental gcd; n is a 256-bit prime."""
    from sympy import factorint, isprime

    g = abs(g)
    if g == 0:
        raise RuntimeError("nullspace relations produced zero gcd")

    if g.bit_length() == 256 and g > max(states) and bool(isprime(g)):
        return g

    fac = factorint(g)
    candidates = []
    for p in fac:
        p = int(p)
        if p.bit_length() == 256 and p > max(states) and bool(isprime(p)):
            candidates.append(p)

    if len(candidates) != 1:
        raise RuntimeError(
            f"could not identify unique 256-bit prime modulus from gcd; "
            f"gcd bits={g.bit_length()}, candidates={candidates}"
        )
    return candidates[0]


def solve_linear_mod(rows: Sequence[Sequence[int]], rhs: Sequence[int], p: int) -> List[int]:
    """Solve an overdetermined full-column-rank system A*x=b over prime field F_p."""
    m = len(rows)
    nvars = len(rows[0])
    mat = [[int(x) % p for x in rows[r]] + [int(rhs[r]) % p] for r in range(m)]

    pivot_row = 0
    pivot_for_col = [-1] * nvars
    for col in range(nvars):
        pivot = next((r for r in range(pivot_row, m) if mat[r][col] % p), None)
        if pivot is None:
            raise RuntimeError(f"rank deficiency at column {col}")
        mat[pivot_row], mat[pivot] = mat[pivot], mat[pivot_row]

        inv = pow(mat[pivot_row][col], -1, p)
        mat[pivot_row] = [(x * inv) % p for x in mat[pivot_row]]

        for r in range(m):
            if r == pivot_row:
                continue
            f = mat[r][col] % p
            if f:
                mat[r] = [(mat[r][c] - f * mat[pivot_row][c]) % p for c in range(nvars + 1)]

        pivot_for_col[col] = pivot_row
        pivot_row += 1

    # Extra equations must reduce to 0 = 0.
    for r in range(pivot_row, m):
        if any(mat[r][c] % p for c in range(nvars)) or mat[r][-1] % p:
            raise RuntimeError("inconsistent modular system")

    x = [mat[pivot_for_col[c]][-1] % p for c in range(nvars)]
    return x


def recover_parameters(ciphertexts: Sequence[str]) -> Tuple[int, int]:
    """Recover n and d = c^1337 mod n from the first 23 known-message outputs."""
    rows, states, _ = build_public_equations(ciphertexts)

    left_null = _primitive_integer_null_vectors(rows)
    multiples = [abs(sum(v[j] * states[j] for j in range(23))) for v in left_null]
    g = math.gcd(*multiples)
    n = _extract_256bit_prime_modulus(g, states)

    solution = solve_linear_mod(rows, states, n)
    d = solution[-1]

    # Independent equation check against all 23 observations.
    for row, s in zip(rows, states):
        if sum(row[i] * solution[i] for i in range(21)) % n != s:
            raise RuntimeError("recovered parameters fail original equation")

    return n, d


# ---------------- MT19937 seed-state inversion ----------------

def _f1(x: int) -> int:
    return ((x ^ (x >> 30)) * 1664525) & MASK32


def _f2(x: int) -> int:
    return ((x ^ (x >> 30)) * 1566083941) & MASK32


def _init_genrand(seed: int = 19650218) -> List[int]:
    mt = [0] * N
    mt[0] = seed & MASK32
    for i in range(1, N):
        mt[i] = (1812433253 * (mt[i - 1] ^ (mt[i - 1] >> 30)) + i) & MASK32
    return mt


def _undo_right_xor(y: int, shift: int) -> int:
    x = y & MASK32
    for _ in range(10):
        x = y ^ (x >> shift)
    return x & MASK32


def _undo_left_xor_mask(y: int, shift: int, mask: int) -> int:
    x = y & MASK32
    for _ in range(10):
        x = y ^ ((x << shift) & mask)
    return x & MASK32


def _untemper(y: int) -> int:
    y = _undo_right_xor(y, 18)
    y = _undo_left_xor_mask(y, 15, 0xEFC60000)
    y = _undo_left_xor_mask(y, 7, 0x9D2C5680)
    y = _undo_right_xor(y, 11)
    return y & MASK32


def _seed_words_for_pretwist_state(target: Sequence[int]) -> List[int]:
    """Invert CPython's init_by_array for a desired 624-word pre-twist state."""
    if len(target) != N or target[0] != 0x80000000:
        raise ValueError("invalid target MT state")

    T = list(target)

    # Invert the second init_by_array loop.
    # After the first 624 iterations, i == 2. Therefore the second loop updates
    # mt[2]..mt[623], wraps, and updates mt[1] last.
    U = [0] * N
    U[1] = ((T[1] + 1) & MASK32) ^ _f2(T[623])
    prev = U[1]
    for i in range(2, 624):
        U[i] = ((T[i] + i) & MASK32) ^ _f2(prev)
        prev = T[i]
    U[0] = U[623]  # wrap invariant from the first loop

    # Invert the first loop. mt[1] is touched twice, so choose its intermediate
    # value V1 freely; this gives us enough freedom to ensure the top seed limb
    # is nonzero, keeping key length exactly 624 words.
    S = _init_genrand()
    for V1 in range(1, 1 << 16):
        key = [0] * N
        key[0] = (V1 - (S[1] ^ _f1(S[0]))) & MASK32

        prev = V1
        for i in range(2, 624):
            j = i - 1
            key[j] = (U[i] - (S[i] ^ _f1(prev)) - j) & MASK32
            prev = U[i]

        key[623] = (U[1] - (V1 ^ _f1(U[623])) - 623) & MASK32
        if key[623] != 0:
            return key

    raise RuntimeError("failed to choose a nonzero top seed word")


def forge_seed(n: int) -> int:
    """
    Forge an integer seed so the first 20 getrandbits(256) calls are:
        r[0] = 0
        r[i] = n - i  (1 <= i < 20)
    Thus (r[i] + i) is 0 or n, and every unknown a[i] term vanishes mod n.
    """
    targets = [0] + [n - i for i in range(1, 20)]

    # CPython getrandbits(256) concatenates eight generated 32-bit words in
    # little-endian limb order: first MT output is the least-significant limb.
    out_words: List[int] = []
    for x in targets:
        out_words.extend((x >> (32 * j)) & MASK32 for j in range(8))

    # We only constrain the first 160 post-twist words. For i < 227,
    # twist[i] depends on pre[i], pre[i+1], pre[i+397]. Choose the low words
    # simply, then solve pre[i+397] directly.
    pretwist = [0] * N
    pretwist[0] = 0x80000000
    for i, tempered_word in enumerate(out_words):
        desired_post = _untemper(tempered_word)
        y = (pretwist[i] & UPPER_MASK) | (pretwist[i + 1] & LOWER_MASK)
        mix = (y >> 1) ^ (MATRIX_A if (y & 1) else 0)
        pretwist[i + M] = (desired_post ^ mix) & MASK32

    key_words = _seed_words_for_pretwist_state(pretwist)
    seed = sum(w << (32 * j) for j, w in enumerate(key_words))

    # Local proof that the forged decimal integer drives CPython exactly as needed.
    check_rng = random.Random(seed)
    got = [check_rng.getrandbits(256) for _ in range(20)]
    if got != targets:
        raise RuntimeError("forged Python seed failed local MT19937 verification")

    return seed


def recover_secret(encrypted_secret_hex: str, d: int) -> bytes:
    ct = bytes.fromhex(encrypted_secret_hex.strip())
    if len(ct) != 32:
        raise ValueError("Encrypted secret must be exactly 32 bytes")
    return xor_bytes(ct, d.to_bytes(32, "big"))


def decrypt_flag(encrypted_flag_hex: str, secret: bytes) -> bytes:
    ct = bytes.fromhex(encrypted_flag_hex.strip())
    key = hashlib.sha256(secret).digest()

    try:
        from Crypto.Cipher import AES  # type: ignore
        from Crypto.Util.Padding import unpad  # type: ignore
        return unpad(AES.new(key, AES.MODE_ECB).decrypt(ct), 16)
    except ModuleNotFoundError:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        dec = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
        padded = dec.update(ct) + dec.finalize()
        padlen = padded[-1]
        if padlen < 1 or padlen > 16 or padded[-padlen:] != bytes([padlen]) * padlen:
            raise ValueError("bad PKCS#7 padding after AES decrypt")
        return padded[:-padlen]



# ---------------- live remote exploit ----------------

def _recv_until(sock: socket.socket, marker: bytes, timeout: float = 20.0) -> bytes:
    sock.settimeout(timeout)
    data = b""
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data


def _parse_initial_banner(text: str) -> Tuple[str, List[str]]:
    m = re.search(r"Encrypted flag:\s*([0-9a-fA-F]+)", text)
    if not m:
        raise RuntimeError("could not parse Encrypted flag from remote banner")
    flag_ct = m.group(1)
    cts = re.findall(r"Ciphertext:\s*([0-9a-fA-F]+)", text)
    if len(cts) < 23:
        raise RuntimeError(f"need 23 initial ciphertexts, got {len(cts)}")
    return flag_ct, cts[:23]


def run_remote(host: str, port: int) -> None:
    """
    Connect to the challenge once and keep the same socket open while computing.
    This is important because each reconnect creates a fresh random instance.
    """
    with socket.create_connection((host, port), timeout=20.0) as sock:
        banner = _recv_until(sock, b"Enter new seed:")
        text = banner.decode("utf-8", errors="replace")
        print(text, end="" if text.endswith("\n") else "\n")

        flag_ct, cts = _parse_initial_banner(text)
        print(f"[+] parsed encrypted flag and {len(cts)} known-message ciphertexts")
        print("[+] recovering n and d...")
        n, d = recover_parameters(cts)
        print(f"[+] n = {n}")
        print(f"[+] d = {d}")

        print("[+] forging Python random seed...")
        seed = forge_seed(n)
        print(f"[+] seed bits = {seed.bit_length()}, decimal digits = {len(str(seed))}")

        # Send forged seed, then empty plaintext hex. Empty plaintext consumes no OTP
        # output before the server reset(), so the final Encrypted secret uses our
        # first forged getrandbits(256) block.
        sock.sendall(str(seed).encode() + b"\n")
        prompt2 = _recv_until(sock, b"Enter your plaintext(hex):")
        print(prompt2.decode("utf-8", errors="replace"), end="")
        sock.sendall(b"\n")

        sock.settimeout(20.0)
        rest = b""
        while True:
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                break
            if not chunk:
                break
            rest += chunk
        out = rest.decode("utf-8", errors="replace")
        print(out, end="" if out.endswith("\n") else "\n")

        m = re.search(r"Encrypted secret:\s*([0-9a-fA-F]+)", out)
        if not m:
            raise RuntimeError("could not parse Encrypted secret from remote output")

        secret_ct = m.group(1)
        secret = recover_secret(secret_ct, d)
        flag = decrypt_flag(flag_ct, secret)
        print(f"[+] secret = {secret.hex()}")
        print(f"[+] FLAG = {flag.decode(errors='replace')}")

# ---------------- local equivalent server for proof ----------------

def _rand_256() -> int:
    return int.from_bytes(os.urandom(32), "big")


def _self_test() -> None:
    from sympy import randprime

    flag = b"flag{fake_flag}"
    secret = os.urandom(32)
    n_true = int(randprime(1 << 255, 1 << 256))
    a = [_rand_256() for _ in range(20)]
    c = _rand_256()
    d_true = pow(c, 1337, n_true)

    # AES-ECB flag encryption, matching chall.py.
    key = hashlib.sha256(secret).digest()
    padlen = 16 - (len(flag) % 16)
    padded = flag + bytes([padlen]) * padlen
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        enc = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
        flag_ct = enc.update(padded) + enc.finalize()
    except ModuleNotFoundError:
        from Crypto.Cipher import AES  # type: ignore
        flag_ct = AES.new(key, AES.MODE_ECB).encrypt(padded)

    # First phase: 23 deterministic known-message OTP outputs.
    rng = random.Random(1337)
    cts: List[str] = []
    for _ in range(23):
        pt = rng.choice(MSGS)
        coeff = [rng.getrandbits(256) + i for i in range(20)]
        state = (sum(coeff[i] * a[i] for i in range(20)) + d_true) % n_true
        cts.append(xor_bytes(pt, state.to_bytes(32, "big")).hex())

    n, d = recover_parameters(cts)
    assert n == n_true
    assert d == d_true

    seed = forge_seed(n)

    # User sends empty plaintext => no RNG consumed before the second reset.
    rng2 = random.Random(seed)
    a2 = [_rand_256() for _ in range(20)]  # fresh reset values, intentionally unknown to solver
    coeff2 = [rng2.getrandbits(256) + i for i in range(20)]
    state2 = (sum(coeff2[i] * a2[i] for i in range(20)) + d_true) % n_true
    assert state2 == d_true

    secret_ct = xor_bytes(secret, state2.to_bytes(32, "big"))
    recovered_secret = recover_secret(secret_ct.hex(), d)
    recovered_flag = decrypt_flag(flag_ct.hex(), recovered_secret)

    print(f"[+] recovered n: {n}")
    print(f"[+] recovered d: {d}")
    print(f"[+] forged seed bits: {seed.bit_length()}")
    print(f"[+] forged seed decimal digits: {len(str(seed))}")
    print(f"[+] secret recovered: {recovered_secret == secret}")
    print(f"[+] flag: {recovered_flag.decode(errors='replace')}")
    print("[+] full local exploit verified")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", help="run complete local proof-of-concept")
    ap.add_argument("--remote", nargs=2, metavar=("HOST", "PORT"), help="exploit a live remote service, e.g. --remote mta-ctf-60.id.vn 6007")
    ap.add_argument("--transcript", help="text file containing one Encrypted flag and 23 Ciphertext lines")
    ap.add_argument("--encrypted-secret", help="32-byte encrypted secret hex from the final line")
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    if args.remote:
        host, port_s = args.remote
        run_remote(host, int(port_s))
        return

    if not args.transcript:
        ap.error("use --self-test, --remote HOST PORT, or --transcript FILE")

    flag_ct = None
    cts: List[str] = []
    with open(args.transcript, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if line.startswith("Encrypted flag:"):
                flag_ct = line.split(":", 1)[1].strip()
            elif line.startswith("Ciphertext:") and len(cts) < 23:
                cts.append(line.split(":", 1)[1].strip())

    if flag_ct is None or len(cts) != 23:
        raise SystemExit("transcript must contain Encrypted flag and exactly 23 initial Ciphertext lines")

    n, d = recover_parameters(cts)
    seed = forge_seed(n)
    print(f"n = {n}")
    print(f"d = {d}")
    print(f"forged_seed = {seed}")
    print("plaintext_hex =   # EMPTY STRING: just press Enter")

    if args.encrypted_secret:
        secret = recover_secret(args.encrypted_secret, d)
        flag = decrypt_flag(flag_ct, secret)
        print(f"secret = {secret.hex()}")
        print(f"flag = {flag.decode(errors='replace')}")


if __name__ == "__main__":
    main()
