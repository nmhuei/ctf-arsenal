#!/usr/bin/env python3
import json
import socket
import re
import hashlib
import random
import string
from Crypto.Util.number import bytes_to_long, long_to_bytes, isPrime

HOST = "socket.cryptohack.org"
PORT = 13431
BITS = 2 << 9  # 1024
G = 2


def recv_until_json_or_banner(f):
    """Read one server line. CryptoHack listener sends banner first, then JSON lines."""
    line = f.readline()
    if not line:
        raise EOFError("server closed connection")
    return line.decode(errors="replace").strip()


def send_json(f, obj):
    f.write((json.dumps(obj) + "\n").encode())
    f.flush()
    line = recv_until_json_or_banner(f)
    try:
        return json.loads(line)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Expected JSON, got: {line!r}") from e


def get_prime_from_seed(nonce: bytes, seed: bytes) -> int:
    """Reproduce server Challenge.getPrime() after Challenge.refresh(seed)."""
    R = random.Random(nonce + seed)
    while True:
        n = R.getrandbits(BITS) | 1
        if isPrime(n, randfunc=lambda x: long_to_bytes(R.getrandbits(x))):
            return n


def c_candidates(t: int, y: int):
    """Server challenge hash uses only R.randint(2, BITS), so brute force it."""
    out = []
    for z in range(2, BITS + 1):
        c = bytes_to_long(hashlib.sha3_256(long_to_bytes(t ^ y ^ G ^ z)).digest())
        out.append(c)
    return out


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def undo_xor_nonce(x: int, nonce: bytes) -> bytes:
    # FLAG is 38 bytes, one non-printable byte is inserted => 39 bytes encoded.
    s = long_to_bytes(x, 39)
    return s[:7] + xor(s[7:-1], nonce) + s[-1:]


def strip_inserted_nonprintable(raw: bytes) -> bytes:
    for i, b in enumerate(raw):
        if chr(b) not in string.printable:
            cand = raw[:i] + raw[i + 1:]
            if cand.startswith(b"crypto{") and cand.endswith(b"}") and len(cand) == 38:
                return cand

    # Fallback: try removing any byte, useful if terminal/locale makes printable odd.
    for i in range(len(raw)):
        cand = raw[:i] + raw[i + 1:]
        if cand.startswith(b"crypto{") and cand.endswith(b"}") and len(cand) == 38:
            return cand
    return raw


def collect_known_prime_proofs(f, nonce: bytes):
    # First proof uses unknown initial seed, but is required before refresh is allowed.
    first = send_json(f, {"option": "get_proof"})
    if "error" in first:
        raise RuntimeError(first)
    print("[*] Burned first unknown-prime proof")

    proofs = []
    # max_turns=4, so after burning one proof we can take exactly 3 known-prime proofs.
    for seed in (b"A" * 8, b"B" * 8, b"C" * 8):
        r = send_json(f, {"option": "refresh", "seed": seed.hex()})
        if "error" in r:
            raise RuntimeError(r)

        p = get_prime_from_seed(nonce, seed)
        pr = send_json(f, {"option": "get_proof"})
        if "error" in pr:
            raise RuntimeError(pr)

        pr["p"] = p
        pr["m"] = p - 1
        pr["cs"] = c_candidates(pr["t"], pr["y"])
        proofs.append(pr)
        print(f"[*] Got proof for seed {seed!r}, p bits={p.bit_length()}")
    return proofs


def recover_secret(proofs, nonce: bytes):
    p1, p2, p3 = proofs

    # r = (v - c*x) mod (p-1)
    # so v = c*x + r - k*(p-1).  Since x is 39 bytes and c is 256 bits,
    # while p is 1024 bits, k is tiny; in practice 0 or 1, but try a few.
    for c1 in p1["cs"]:
        for c2 in p2["cs"]:
            den = c1 - c2
            if den == 0:
                continue
            for k1 in range(4):
                for k2 in range(4):
                    num = (p2["r"] - k2 * p2["m"]) - (p1["r"] - k1 * p1["m"])
                    if num % den:
                        continue
                    x = num // den
                    if not (0 < x < (1 << (39 * 8))):
                        continue

                    v12 = c1 * x + p1["r"] - k1 * p1["m"]
                    if v12 != c2 * x + p2["r"] - k2 * p2["m"]:
                        continue

                    for c3 in p3["cs"]:
                        for k3 in range(4):
                            v3 = c3 * x + p3["r"] - k3 * p3["m"]
                            if v12 == v3:
                                raw = undo_xor_nonce(x, nonce)
                                flag = strip_inserted_nonprintable(raw)
                                return flag, raw, (c1, c2, c3), (k1, k2, k3)
    raise RuntimeError("secret not found; increase k range or retry connection")


def main():
    with socket.create_connection((HOST, PORT), timeout=20) as sock:
        f = sock.makefile("rwb", buffering=0)
        banner_lines = []
        for _ in range(5):
            line = f.readline().decode(errors="replace").strip()
            if not line:
                break
            banner_lines.append(line)
            if "nonce" in line.lower() or any(len(part) == 62 for part in line.split()):
                break
        banner_text = "\n".join(banner_lines)
        print("[*] Banner received:")
        print(banner_text)

        m = re.search(r"([0-9a-f]{62})", banner_text)
        if not m:
            raise RuntimeError("Could not parse 31-byte nonce from banner")
        nonce = bytes.fromhex(m.group(1))
        print(f"[*] nonce = {nonce.hex()}")

        proofs = collect_known_prime_proofs(f, nonce)
        flag, raw, cs, ks = recover_secret(proofs, nonce)
        print(f"[*] raw with inserted byte = {raw!r}")
        print(f"[*] wraps k = {ks}")
        print(flag.decode(errors="replace"))


if __name__ == "__main__":
    main()
