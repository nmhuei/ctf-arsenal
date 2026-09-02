#!/usr/bin/env python3
import json
import time
import hashlib
import hmac
from pathlib import Path
from fpylll import IntegerMatrix, LLL, BKZ

# Challenge parameters
n = 128
q = 268435361
w = 80
d = b"\x3a\x91\xf0\x7d\x14\x68\xbc\x29"
r = 5


def sh(a, k):
    k %= 2 * n
    s = -1 if k >= n else 1
    if k >= n:
        k -= n
    b = [0] * n
    for i in range(n):
        if i + k < n:
            b[i + k] = s * a[i]
        else:
            b[i + k - n] = -s * a[i]
    return b


def ky(a, b, s):
    u = min(tuple(sh(a, i) + sh(b, i)) for i in range(2 * n))
    return hashlib.sha3_256(d + s + bytes(i + 1 for i in u)).digest()


def dc(a, b, h, z):
    s, c, t = bytes.fromhex(z["S"]), bytes.fromhex(z["C"]), bytes.fromhex(z["T"])
    k = ky(a, b, s)
    u = json.dumps({"N": n, "Q": q, "H": h}, sort_keys=True, separators=(",", ":")).encode()
    if not hmac.compare_digest(t, hmac.new(k, d + u + s + c, hashlib.sha256).digest()[:16]):
        raise ValueError("HMAC verification failed")
    z_stream = hashlib.shake_256(d + k + s).digest(len(c))
    return bytes(i ^ j for i, j in zip(c, z_stream))


def pm(a, b):
    c = [0] * n
    for i in range(n):
        for j in range(n):
            if i + j < n:
                c[i + j] = (c[i + j] + a[i] * b[j]) % q
            else:
                c[i + j - n] = (c[i + j - n] - a[i] * b[j]) % q
    return c


def get_H_matrix(h, n):
    H = []
    for i in range(n):
        row = [0] * n
        for j in range(n):
            if i + j < n:
                row[i + j] = (row[i + j] + h[j]) % q
            else:
                row[i + j - n] = (row[i + j - n] - h[j]) % q
        H.append(row)
    return H


def solve():
    enc_path = Path(__file__).resolve().parent.parent / "challenge" / "Fence" / "flag.enc"
    with open(enc_path, "r", encoding="utf-8") as f:
        enc_data = json.load(f)

    hs = enc_data["H"]
    cs = enc_data["C"]

    decrypted_shares = []

    print("[*] Starting Fence Solver (NTRU uSVP with BKZ-20 on dim 176)...")
    total_start = time.time()

    for idx in range(r):
        h = hs[idx]
        c_pkg = cs[idx]
        print(f"[*] Solving share {idx+1}/{r}...")
        t0 = time.time()

        H = get_H_matrix(h, n)
        m_eq = 48
        dim = m_eq + n
        M = IntegerMatrix(dim, dim)
        for i in range(m_eq):
            M[i, i] = q
        for i in range(n):
            for j in range(m_eq):
                M[m_eq + i, j] = H[i][j]
            M[m_eq + i, m_eq + i] = 1

        LLL.reduction(M)
        BKZ.reduction(M, BKZ.Param(block_size=20))

        a_found = None
        b_found = None
        for row_idx in range(dim):
            row = [M[row_idx, col] for col in range(dim)]
            a_cand = row[m_eq:]
            if set(a_cand).issubset({-1, 0, 1}) and sum(abs(x) for x in a_cand) == w:
                b_cand_raw = pm(a_cand, h)
                b_cand = [(x if x <= q // 2 else x - q) for x in b_cand_raw]
                if set(b_cand).issubset({-1, 0, 1}) and sum(abs(x) for x in b_cand) == w:
                    a_found = a_cand
                    b_found = b_cand
                    break

        if not a_found:
            raise RuntimeError(f"Failed to find private polynomials for share {idx+1}!")

        print(f"[+] Share {idx+1} recovered in {time.time() - t0:.2f}s!")
        m = dc(a_found, b_found, h, c_pkg)
        decrypted_shares.append(m)

    flag = bytes([0] * len(decrypted_shares[0]))
    for m in decrypted_shares:
        flag = bytes(x ^ y for x, y in zip(flag, m))

    flag_str = flag.decode("utf-8", errors="replace")
    print(f"\n[+] Total solve time: {time.time() - total_start:.2f}s")
    print(f"[+] Recovered Flag: {flag_str}")
    return flag_str


if __name__ == "__main__":
    solve()
