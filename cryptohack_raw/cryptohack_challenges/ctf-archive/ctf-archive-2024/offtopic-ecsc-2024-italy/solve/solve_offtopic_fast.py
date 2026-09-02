#!/usr/bin/env python3
import socket
import sys

p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
q = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
a = (p - 3) % p
Gx = 0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296
Gy = 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5
G = (Gx, Gy)


def inv_mod(n):
    return pow(n % p, -1, p)


def neg(P):
    if P is None:
        return None
    x, y = P
    return (x, (-y) % p)


def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = ((3 * x1 * x1 + a) * inv_mod(2 * y1)) % p
    else:
        lam = ((y2 - y1) * inv_mod(x2 - x1)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def mul(n, P):
    n %= q
    R = None
    A = P
    while n:
        if n & 1:
            R = add(R, A)
        A = add(A, A)
        n >>= 1
    return R


def small_mul(n):
    if n == 0:
        return None
    if n < 0:
        return neg(small_mul(-n))
    R = None
    for _ in range(n):
        R = add(R, G)
    return R


def pt_json(prefix, P):
    return f'"{prefix}x":{P[0]},"{prefix}y":{P[1]}'


def parse_json_object(buf):
    start = buf.find(b"{")
    if start < 0:
        return None, buf
    end = buf.find(b"}", start)
    if end < 0:
        return None, buf
    body = buf[start + 1:end]
    vals = []
    i = 0
    n = len(body)
    while i < n:
        if body[i] == 58:
            i += 1
            while i < n and not (48 <= body[i] <= 57):
                i += 1
            j = i
            while j < n and 48 <= body[j] <= 57:
                j += 1
            if j == i:
                raise RuntimeError(f"bad json body: {body!r}")
            vals.append(int(body[i:j]))
            i = j
        else:
            i += 1
    if len(vals) != 4:
        raise RuntimeError(f"bad json body: {body!r}")
    return vals, buf[end + 1:]


def main():
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} host port", file=sys.stderr)
        sys.exit(1)

    host, port = sys.argv[1], int(sys.argv[2])

    x_secret = q - 1
    k_plain = 10
    r_choice = 1

    H = mul(x_secret, G)
    C_R = mul(r_choice, G)
    C_S = add(mul(r_choice, H), small_mul(k_plain))

    pk_line = ("{" + pt_json("H", H) + "}\n").encode()
    ct_line = ("{" + pt_json("R", C_R) + "," + pt_json("S", C_S) + "}\n").encode()

    answers = {}
    answers_last = {}
    for m0 in range(10):
        for m1 in range(10):
            coeff = (1 - k_plain) * m0 + k_plain * m1
            key = small_mul(coeff)
            ans = f'{{"m0":{m0},"m1":{m1}}}\n'.encode()
            answers[key] = ans + ct_line
            answers_last[key] = ans

    s = socket.create_connection((host, port), timeout=10.0)
    s.settimeout(15.0)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    for opt in (getattr(socket, "TCP_QUICKACK", None), getattr(socket, "TCP_FASTOPEN_CONNECT", None)):
        if opt is not None:
            try:
                s.setsockopt(socket.IPPROTO_TCP, opt, 1)
            except OSError:
                pass

    buf = b""
    s.sendall(pk_line + ct_line)
    try:
        for i in range(128):
            vals = None
            while vals is None:
                chunk = s.recv(65536)
                if not chunk:
                    raise EOFError(f"remote closed; buffered={buf[-512:]!r}")
                buf += chunk
                vals, buf = parse_json_object(buf)
            Rx, Ry, Sx, Sy = vals
            key = add((Sx, Sy), (Rx, Ry))
            payload = answers_last[key] if i == 127 else answers[key]
            s.sendall(payload)
            try:
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
            except (AttributeError, OSError):
                pass
        out = b""
        while True:
            try:
                chunk = s.recv(65536)
            except socket.timeout:
                break
            if not chunk:
                break
            out += chunk
        if out:
            sys.stdout.write(out.decode(errors="replace"))
    finally:
        s.close()


if __name__ == "__main__":
    main()
