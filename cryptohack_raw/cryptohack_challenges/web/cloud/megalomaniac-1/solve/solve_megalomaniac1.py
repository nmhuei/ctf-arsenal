#!/usr/bin/env python3
import argparse
import ast
import hashlib
import json
import math
import random
import re
import socket
import sys
import time
from decimal import Decimal, getcontext

B = 1 << 128

# ---------------- JSON socket helpers ----------------
class JsonSock:
    def __init__(self, host, port, timeout=20):
        self.s = socket.create_connection((host, port), timeout=timeout)
        self.s.settimeout(timeout)
        self.buf = b""

    def recv_some(self, max_wait=2.0):
        end = time.time() + max_wait
        chunks = []
        while time.time() < end:
            try:
                part = self.s.recv(4096)
                if not part:
                    break
                chunks.append(part)
                self.buf += part
                # CryptoHack banner usually arrives in one shot.
                if b"}\n" in self.buf or b"}\r\n" in self.buf:
                    break
            except socket.timeout:
                break
        return b"".join(chunks)

    def send_json(self, obj):
        line = json.dumps(obj, separators=(",", ":")).encode() + b"\n"
        self.s.sendall(line)

    def recv_json(self):
        while b"\n" not in self.buf:
            part = self.s.recv(4096)
            if not part:
                raise EOFError("socket closed")
            self.buf += part
        line, self.buf = self.buf.split(b"\n", 1)
        # Skip non-json text lines if any.
        while line and not line.lstrip().startswith(b"{"):
            if b"\n" not in self.buf:
                part = self.s.recv(4096)
                if not part:
                    raise EOFError("socket closed")
                self.buf += part
            line, self.buf = self.buf.split(b"\n", 1)
        return json.loads(line.decode())

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass


def parse_initial_material(text):
    # Find the JSON object containing crypto material in the initial banner.
    for line in text.decode(errors="replace").splitlines():
        line = line.strip()
        if line.startswith("{") and "share_key_enc" in line:
            return json.loads(line)
    m = re.search(r"\{.*share_key_enc.*\}", text.decode(errors="replace"), re.S)
    if not m:
        raise ValueError("could not find registration material JSON")
    return json.loads(m.group(0))

# ---------------- Number/crypto helpers ----------------
def long_to_bytes(n):
    if n == 0:
        return b"\x00"
    return n.to_bytes((n.bit_length() + 7) // 8, "big")


def aes_ecb_decrypt(key, ct):
    try:
        from Crypto.Cipher import AES
        return AES.new(key, AES.MODE_ECB).decrypt(ct)
    except Exception:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        dec = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
        return dec.update(ct) + dec.finalize()


def pkcs7_unpad(data, block_size=16):
    if not data:
        raise ValueError("empty data")
    k = data[-1]
    if k < 1 or k > block_size or data[-k:] != bytes([k]) * k:
        raise ValueError("invalid PKCS#7 padding")
    return data[:-k]

# ---------------- Decimal LLL + Coppersmith linear ----------------
def lll_decimal(basis, delta=Decimal("0.75"), prec=900):
    getcontext().prec = prec
    Bv = [list(map(int, row)) for row in basis]
    n = len(Bv)
    dim = len(Bv[0])

    def gram_schmidt():
        bstar = [[Decimal(0)] * dim for _ in range(n)]
        mu = [[Decimal(0)] * n for _ in range(n)]
        norm = [Decimal(0)] * n
        for i in range(n):
            bstar[i] = [Decimal(z) for z in Bv[i]]
            for j in range(i):
                if norm[j] != 0:
                    mu[i][j] = sum(Decimal(Bv[i][k]) * bstar[j][k] for k in range(dim)) / norm[j]
                    if mu[i][j]:
                        for k in range(dim):
                            bstar[i][k] -= mu[i][j] * bstar[j][k]
            norm[i] = sum(z * z for z in bstar[i])
        return mu, norm

    k = 1
    mu, norm = gram_schmidt()
    it = 0
    while k < n:
        it += 1
        for j in range(k - 1, -1, -1):
            q = int(mu[k][j].to_integral_value(rounding="ROUND_HALF_EVEN"))
            if q:
                Bv[k] = [Bv[k][i] - q * Bv[j][i] for i in range(dim)]
                mu, norm = gram_schmidt()
        if norm[k] >= (delta - mu[k][k - 1] * mu[k][k - 1]) * norm[k - 1]:
            k += 1
        else:
            Bv[k], Bv[k - 1] = Bv[k - 1], Bv[k]
            mu, norm = gram_schmidt()
            k = max(k - 1, 1)
        if it > 10000:
            raise RuntimeError("LLL did not converge")
    return Bv


def find_integer_roots_with_sympy(coeffs):
    # coeffs are ascending: c0 + c1*x + ...
    try:
        import sympy as sp
        x = sp.symbols("x")
        poly = sp.Poly(sum(int(coeffs[i]) * x ** i for i in range(len(coeffs))), x, domain=sp.ZZ)
        roots = []
        if poly.degree() == 1:
            a = poly.nth(1)
            b = poly.nth(0)
            if a and (-b) % a == 0:
                roots.append(int((-b) // a))
        try:
            for r, _mult in poly.ground_roots().items():
                roots.append(int(r))
        except Exception:
            pass
        return list(dict.fromkeys(roots))
    except Exception:
        return []


def coppersmith_linear_factor(M, N, X=B, prec=900):
    # Coppersmith for f(x)=M+x, with small x<X and f(x)==0 mod p, p≈sqrt(N).
    # m=2,t=2 basis, f is monic degree 1.
    rows = [
        [N * N, 0, 0, 0],
        [N * M, N * X, 0, 0],
        [M * M, 2 * M * X, X * X, 0],
        [0, M * M * X, 2 * M * X * X, X * X * X],
    ]
    red = lll_decimal(rows, prec=prec)
    for row in red:
        coeffs = [row[i] // (X ** i) for i in range(len(row))]
        while coeffs and coeffs[-1] == 0:
            coeffs.pop()
        if len(coeffs) <= 1:
            continue
        for r in find_integer_roots_with_sympy(coeffs):
            if 0 <= r < X:
                g = math.gcd(M + r, N)
                if 1 < g < N:
                    return g, r
    raise RuntimeError("Coppersmith failed to recover factor")

# ---------------- Exploit ----------------
def make_faulty_share_key_enc(share_key_enc_hex, replacement_pairs=None):
    data = bytes.fromhex(share_key_enc_hex)
    if len(data) % 16 != 0:
        raise ValueError("share_key_enc length is not multiple of 16")
    blocks = [data[i:i+16] for i in range(0, len(data), 16)]
    if len(blocks) != 41:
        raise ValueError(f"unexpected block count {len(blocks)}; expected 41")
    idx = list(range(41))
    # Parser-critical blocks remain fixed: 0,8,16,32,40.
    # Corrupt q only by replacing one middle q block. p,d,u remain original.
    if replacement_pairs is None:
        replacement_pairs = [(9, 1)]
    for dst, src in replacement_pairs:
        idx[dst] = src
    return b"".join(blocks[i] for i in idx).hex()


def recover_factor_from_fault(js, material, verbose=True):
    n, e = map(int, material["share_key_pub"])
    master_key_enc = material["master_key_enc"]
    faulty_share = make_faulty_share_key_enc(material["share_key_enc"])

    # Start login.
    js.send_json({"action": "wait_login"})
    r = js.recv_json()
    if verbose:
        print("[+] wait_login:", r)

    # Choose s definitely smaller than a 1024-bit prime p.
    s = random.randrange(1 << 500, 1 << 501)
    c = pow(s, e, n)
    sid_enc = long_to_bytes(c).rjust(256, b"\x00").hex()

    js.send_json({
        "action": "send_challenge",
        "SID_enc": sid_enc,
        "share_key_enc": faulty_share,
        "master_key_enc": master_key_enc,
    })
    r = js.recv_json()
    if "SID" not in r:
        raise RuntimeError(f"faulty login failed: {r}")
    Y = int(r["SID"], 16) if r["SID"] else 0
    if verbose:
        print(f"[+] got truncated faulty plaintext: {len(r['SID'])//2} bytes visible")

    M = Y * B - s
    p, missing_low = coppersmith_linear_factor(M, n, B)
    q = n // p
    if p * q != n:
        raise RuntimeError("bad factorization")
    if verbose:
        print("[+] recovered factor p bits:", p.bit_length())
        print("[+] recovered factor q bits:", q.bit_length())
        print("[+] missing low 16 bytes:", hex(missing_low))
    return p, q, n, e


def get_encrypted_flag(js):
    js.send_json({"action": "get_encrypted_flag"})
    r = js.recv_json()
    if "encrypted_flag" not in r:
        raise RuntimeError(f"get_encrypted_flag failed: {r}")
    return bytes.fromhex(r["encrypted_flag"])


def decrypt_flag(enc_flag, p, q):
    for a, b in [(p, q), (q, p)]:
        key = hashlib.sha256(long_to_bytes(a) + long_to_bytes(b)).digest()
        pt = pkcs7_unpad(aes_ecb_decrypt(key, enc_flag), 16)
        if pt.startswith(b"crypto{") and pt.endswith(b"}"):
            return pt.decode(), key.hex(), (a, b)
    raise RuntimeError("decryption failed with both p||q and q||p")


def solve(host, port, timeout=20):
    js = JsonSock(host, port, timeout=timeout)
    try:
        banner = js.recv_some(max_wait=2.0)
        print(banner.decode(errors="replace"), end="")
        material = parse_initial_material(banner)
        print("[+] parsed registration material")
        p, q, n, e = recover_factor_from_fault(js, material)
        enc_flag = get_encrypted_flag(js)
        flag, aes_key_hex, ordered = decrypt_flag(enc_flag, p, q)
        print("[+] encrypted_flag:", enc_flag.hex())
        print("[+] SHA256(p||q) AES key:", aes_key_hex)
        print("[+] proof: p*q == n ->", ordered[0] * ordered[1] == n)
        print("FLAG:", flag)
        return flag
    finally:
        js.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("host", nargs="?", default="socket.cryptohack.org")
    ap.add_argument("port", nargs="?", type=int, default=13408)
    ap.add_argument("--timeout", type=int, default=20)
    args = ap.parse_args()
    solve(args.host, args.port, args.timeout)

if __name__ == "__main__":
    main()
