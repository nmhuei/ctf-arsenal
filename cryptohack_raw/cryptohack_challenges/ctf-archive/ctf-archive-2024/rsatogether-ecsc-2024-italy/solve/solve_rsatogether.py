#!/usr/bin/env python3
import socket
import re
import sys
from fractions import Fraction
from math import gcd, isqrt

M = 100


def build_relation_constants():
    """
    Let B_j = P(j) for j=0..99 where B_0=d and deg(P)<100.
    The leaked share for input t (so k=t+1 total points) is:
        S_{t+1} ≡ (-1)^(t-1) * (t+1) * P(t) mod phi
    for t=1..98, and the same formula also holds for t=99,100,101 because then
    the full degree-99 polynomial is used.

    Interpolating P(100) and P(101) from P(0)..P(99) yields two linear
    relations modulo phi involving d and the 101 leaked values S_2..S_102.
    After multiplying by e and using e*d ≡ 1 (mod phi), each relation becomes
    a known multiple of phi. Their gcd reveals phi up to a tiny cofactor.
    """
    basis = []
    v = [Fraction(0) for _ in range(M)]
    v[0] = Fraction(1)
    basis.append(v)

    # Newton basis -> monomial interpolation coefficients as exact rationals.
    for i in range(1, M):
        v = [Fraction(0) for _ in range(M)]
        v[i] = Fraction(1)
        for k in range(i):
            ik = i ** k
            bk = basis[k]
            for j in range(M):
                v[j] -= ik * bk[j]
        den = i ** i
        for j in range(M):
            v[j] /= den
        basis.append(v)

    def pvec_at(x):
        out = [Fraction(0) for _ in range(M)]
        for i in range(M):
            xi = x ** i
            bi = basis[i]
            for j in range(M):
                out[j] += xi * bi[j]
        return out

    def make_relation(pvec, target_r, target_den, target_sign):
        # pvec dot [P(0),...,P(99)] - target_sign * S_target_r/target_den ≡ 0 mod phi
        # where target_r=101 corresponds to P(100) = -S_101/101,
        # and target_r=102 corresponds to P(101) = +S_102/102.
        terms = []
        A = pvec[0]  # coefficient of d = P(0)
        for j in range(1, M):
            # P(j) = (-1)^(j-1) * S_{j+1} / (j+1) mod phi
            terms.append((j + 1, pvec[j] * ((-1) ** (j - 1)) / (j + 1)))
        terms.append((target_r, Fraction(-target_sign, target_den)))

        L = A.denominator
        for _, fr in terms:
            L = L * fr.denominator // gcd(L, fr.denominator)

        Aint = int(A * L)
        coeffs = {}
        for r, fr in terms:
            coeffs[r] = coeffs.get(r, 0) + int(fr * L)
        return Aint, coeffs

    return (
        make_relation(pvec_at(100), 101, 101, -1),
        make_relation(pvec_at(101), 102, 102, 1),
    )


def connect_ipv4(host, port, timeout=20):
    last = None
    for family, socktype, proto, _, addr in socket.getaddrinfo(host, int(port), socket.AF_INET, socket.SOCK_STREAM):
        s = socket.socket(family, socktype, proto)
        s.settimeout(timeout)
        try:
            s.connect(addr)
            return s
        except OSError as e:
            last = e
            s.close()
    raise last or OSError("could not connect")


def recv_until(sock, token: bytes, timeout=10) -> bytes:
    sock.settimeout(timeout)
    data = b""
    while token not in data:
        chunk = sock.recv(4096)
        if not chunk:
            raise EOFError(f"remote closed before token {token!r}")
        data += chunk
    return data


def recv_all(sock, timeout=5) -> bytes:
    sock.settimeout(timeout)
    chunks = []
    while True:
        try:
            chunk = sock.recv(65536)
        except socket.timeout:
            break
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks)


def recover_phi(n, g):
    g = abs(g)
    h0 = (g + n - 1) // n
    for radius in (0, 8, 500, 200000):
        lo = max(1, h0 - radius)
        hi = h0 + radius
        for h in range(lo, hi + 1):
            if g % h:
                continue
            phi = g // h
            s = n - phi + 1
            D = s * s - 4 * n
            if D < 0:
                continue
            t = isqrt(D)
            if t * t == D and (s + t) % 2 == 0:
                p = (s + t) // 2
                q = (s - t) // 2
                if p * q == n:
                    return phi, p, q
    raise ValueError("Could not recover phi from gcd multiple")


def int_to_bytes(x):
    if x == 0:
        return b"\x00"
    return x.to_bytes((x.bit_length() + 7) // 8, "big")


def solve(host, port):
    print("[*] Precomputing exact interpolation constants...")
    (A1, C1), (A2, C2) = build_relation_constants()

    # Send the entire interaction in one burst to beat the 60-second challenge timeout.
    order = list(range(1, 102))
    lines = [str(order[0])]
    for friends in order[1:]:
        lines.append("2")
        lines.append(str(friends))
    lines.append("3")
    payload = ("\n".join(lines) + "\n").encode()

    with connect_ipv4(host, int(port), timeout=20) as sock:
        # Wait only for the first prompt so we know the service is ready,
        # then pipeline the rest.
        prefix = recv_until(sock, b"private key? ", timeout=10)
        sock.sendall(payload)
        transcript = prefix + recv_all(sock, timeout=8)

    n_m = re.search(rb"(?:^|\n)n\s*=\s*(\d+)", transcript)
    e_m = re.search(rb"(?:^|\n)e\s*=\s*(\d+)", transcript)
    if not n_m or not e_m:
        raise ValueError("Could not parse n/e from transcript:\n" + transcript.decode(errors="replace"))
    n = int(n_m.group(1))
    e = int(e_m.group(1))
    print(f"[*] n bits = {n.bit_length()}, e = {e}")

    shares = [int(x) for x in re.findall(rb"Here is your part:\s*(\d+)", transcript)]
    if len(shares) != 101:
        raise ValueError(f"Expected 101 leaked shares, got {len(shares)}")
    S = {friends + 1: share for friends, share in zip(order, shares)}
    print("[*] Collected all 101 shares within one pipelined session")

    nums = re.findall(rb"\d+", transcript)
    if not nums:
        raise ValueError("Could not parse final ciphertext")
    c = int(nums[-1])
    print("[*] Got final ciphertext")

    B1 = sum(coeff * S[r] for r, coeff in C1.items())
    B2 = sum(coeff * S[r] for r, coeff in C2.items())
    K1 = e * B1 + A1
    K2 = e * B2 + A2
    g = gcd(abs(K1), abs(K2))
    print(f"[*] gcd bits = {g.bit_length()}")

    phi, p, q = recover_phi(n, g)
    print("[*] Factored n")
    d = pow(e, -1, phi)
    pt = int_to_bytes(pow(c, d, n))
    m = re.search(rb"ECSC\{[^}]+\}", pt)
    if m:
        print("FLAG:", m.group(0).decode())
    else:
        print(pt)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} HOST PORT")
        raise SystemExit(1)
    solve(sys.argv[1], sys.argv[2])
