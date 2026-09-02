#!/usr/bin/env sage
# GLP420 (HackTM CTF) solver
# Run local test: sage solve_glp420.sage local
# Run remote    : sage solve_glp420.sage archive.cryptohack.org 26931

import sys
import re
import time
import socket
import hashlib
import secrets

q = 8383489
b = 16383
w = 3
n = 420
D = 2*n + 1
M_EMBED = 1
MSG = b"sign me!"


def center_mod(x, mod=q):
    x = int(x) % mod
    if x > mod//2:
        x -= mod
    return int(x)


def enc3(x):
    return (int(x) % q).to_bytes(3, "big")


def decode_poly_hex(hx):
    raw = bytes.fromhex(hx.decode() if isinstance(hx, bytes) else hx)
    assert len(raw) == 3*n, (len(raw), 3*n)
    return [int.from_bytes(raw[i:i+3], "big") % q for i in range(0, 3*n, 3)]


def encode_poly_hex(poly):
    return b"".join(enc3(c) for c in poly).hex()


def polyhash(poly_mod_q, msg):
    h = hashlib.sha256()
    for c in poly_mod_q:
        h.update(enc3(c))
    h.update(msg)
    return h.digest()


def hash2poly(digest):
    x = int.from_bytes(digest, "big")
    return [1 if ((x >> i) & 1) else 0 for i in range(n)]


def add_mod(a, b_):
    return [(int(x) + int(y)) % q for x, y in zip(a, b_)]


def sub_mod(a, b_):
    return [(int(x) - int(y)) % q for x, y in zip(a, b_)]


def mul_cyclic_mod(a, b_):
    res = [0]*n
    for i, ai in enumerate(a):
        ai = int(ai) % q
        if ai == 0:
            continue
        for j, bj in enumerate(b_):
            bj = int(bj)
            if bj:
                res[(i+j) % n] = (res[(i+j) % n] + ai*bj) % q
    return res


def mul_cyclic_int(a, b_):
    res = [0]*n
    for i, ai in enumerate(a):
        ai = int(ai)
        if ai == 0:
            continue
        for j, bj in enumerate(b_):
            bj = int(bj)
            if bj:
                res[(i+j) % n] += ai*bj
    return res


def verify_key(a, t, s, e):
    if any(x not in (-1, 0, 1) for x in s):
        return False
    if any(x not in (-1, 0, 1) for x in e):
        return False
    lhs = add_mod(mul_cyclic_mod(a, s), e)
    return all((lhs[i] - t[i]) % q == 0 for i in range(n))


def recover_key(a, t, use_bkz=False):
    """Recover ternary s,e from t = a*s + e using Kannan embedding.
       With the target row below, the wanted short row is (-s, e, 1) up to sign.
    """
    print("[*] building %dx%d embedding lattice" % (D, D))
    B = Matrix(ZZ, D, D)

    ac = [center_mod(x) for x in a]
    tc = [center_mod(x) for x in t]

    # Rows generating L = {(u, A*u + q*k)}, where A is cyclic convolution by a.
    # Row i contains column i of the convolution matrix, so row-combination u gives A*u.
    for i in range(n):
        B[i, i] = 1
        for r in range(n):
            B[i, n+r] = ac[(r-i) % n]

    for i in range(n):
        B[n+i, n+i] = q

    # Target row: adding it to -s rows gives (-s, e, 1).
    for r in range(n):
        B[2*n, n+r] = tc[r]
    B[2*n, 2*n] = M_EMBED

    print("[*] reducing lattice with LLL")
    st = time.time()
    try:
        R = B.LLL(delta=0.99, algorithm="fpLLL:wrapper")
    except TypeError:
        R = B.LLL(delta=0.99)
    print("[*] LLL done in %.2fs" % (time.time() - st))

    def scan_rows(Mat):
        for idx in range(Mat.nrows()):
            row = Mat.row(idx)
            last = int(row[2*n])
            if abs(last) != M_EMBED:
                continue
            # Normalize so last is +1.
            rr = [int(row[j]) * last for j in range(D)]  # M=1, last=+-1
            s = [-rr[i] for i in range(n)]
            e = [rr[n+i] for i in range(n)]
            if verify_key(a, t, s, e):
                print("[+] recovered key from row", idx)
                print("[+] wt(s)=%d wt(e)=%d" % (sum(1 for x in s if x), sum(1 for x in e if x)))
                return s, e
        return None

    got = scan_rows(R)
    if got is not None:
        return got

    if use_bkz:
        print("[*] LLL did not expose key; trying BKZ-20")
        st = time.time()
        try:
            R2 = R.BKZ(block_size=20)
        except TypeError:
            R2 = R.BKZ(20)
        print("[*] BKZ done in %.2fs" % (time.time() - st))
        got = scan_rows(R2)
        if got is not None:
            return got

    raise RuntimeError("key not found; retry with use_bkz=True or stronger BKZ block size")


def sign_with_key(a, t, s, e, msg=MSG):
    attempts = 0
    while True:
        attempts += 1
        y1 = [secrets.randbelow(2*b + 1) - b for _ in range(n)]
        y2 = [secrets.randbelow(2*b + 1) - b for _ in range(n)]
        u = add_mod(mul_cyclic_mod(a, y1), y2)
        c = hash2poly(polyhash(u, msg))
        z1 = [x + y for x, y in zip(mul_cyclic_int(s, c), y1)]
        z2 = [x + y for x, y in zip(mul_cyclic_int(e, c), y2)]
        if all(abs(int(x)) <= b-w for x in z1) and all(abs(int(x)) <= b-w for x in z2):
            print("[+] signature sampled after %d attempt(s)" % attempts)
            assert verify_sig(a, t, z1, z2, c, msg)
            return z1, z2, c


def verify_sig(a, t, z1, z2, c, msg=MSG):
    for v in z1 + z2:
        if min(int(v) % q, q - (int(v) % q)) > b-w:
            return False
    lhs = sub_mod(add_mod(mul_cyclic_mod(a, z1), z2), mul_cyclic_mod(t, c))
    d = hash2poly(polyhash(lhs, msg))
    return d == list(c)


def sample_small(K):
    return [secrets.randbelow(2*K + 1) - K for _ in range(n)]


def local_test():
    print("[*] generating local GLP420 instance")
    a = sample_small((q-1)//2)
    s0 = sample_small(1)
    e0 = sample_small(1)
    t = add_mod(mul_cyclic_mod(a, s0), e0)
    s, e = recover_key(a, t, use_bkz=True)
    assert s == s0 and e == e0
    z1, z2, c = sign_with_key(a, t, s, e)
    assert verify_sig(a, t, z1, z2, c)
    print("[+] local ok")
    print("z1 =", encode_poly_hex(z1)[:80] + "...")
    print("z2 =", encode_poly_hex(z2)[:80] + "...")
    print("c  =", encode_poly_hex(c)[:80] + "...")


def recv_until(sock, token):
    data = b""
    while token not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data


def remote(host, port):
    print("[*] connecting to %s:%d" % (host, port))
    sock = socket.create_connection((host, int(port)))
    data = recv_until(sock, b"z1 = ")
    sys.stdout.write(data.decode(errors="replace"))
    a_hex = re.search(rb"a_enc = ([0-9a-f]+)", data).group(1)
    t_hex = re.search(rb"t_enc = ([0-9a-f]+)", data).group(1)
    a = decode_poly_hex(a_hex)
    t = decode_poly_hex(t_hex)

    s, e = recover_key(a, t, use_bkz=True)
    z1, z2, c = sign_with_key(a, t, s, e)

    sock.sendall((encode_poly_hex(z1) + "\n").encode())
    data = recv_until(sock, b"z2 = ")
    sys.stdout.write(data.decode(errors="replace"))
    sock.sendall((encode_poly_hex(z2) + "\n").encode())
    data = recv_until(sock, b"c = ")
    sys.stdout.write(data.decode(errors="replace"))
    sock.sendall((encode_poly_hex(c) + "\n").encode())
    rest = b""
    while True:
        part = sock.recv(4096)
        if not part:
            break
        rest += part
    print(rest.decode(errors="replace"))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "local":
        local_test()
    elif len(sys.argv) == 3:
        remote(sys.argv[1], int(sys.argv[2]))
    else:
        print("usage:")
        print("  sage solve_glp420.sage local")
        print("  sage solve_glp420.sage archive.cryptohack.org 26931")
