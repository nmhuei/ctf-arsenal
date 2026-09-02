#!/usr/bin/env python3
from math import comb, gcd
import socket
import sys

# Challenge polynomials:
#   f = x^13 + 37
#   h = (x+42)^13 + 42
# For every integer x, gcd(f(x), h(x)) divides Res(f,h).
# Work modulo N=Res(f,h), find a linear gcd of f,h in (Z/NZ)[x],
# and use its root as x. This makes both values divisible by N.

n = 13
A = 37
B = 42
C = 42


def bareiss_det(M):
    M = [row[:] for row in M]
    size = len(M)
    sign = 1
    prev = 1
    for k in range(size - 1):
        if M[k][k] == 0:
            for i in range(k + 1, size):
                if M[i][k] != 0:
                    M[k], M[i] = M[i], M[k]
                    sign = -sign
                    break
            else:
                return 0
        pivot = M[k][k]
        for i in range(k + 1, size):
            for j in range(k + 1, size):
                M[i][j] = (M[i][j] * pivot - M[i][k] * M[k][j]) // prev
        prev = pivot
        for i in range(k + 1, size):
            M[i][k] = 0
        for j in range(k + 1, size):
            M[k][j] = 0
    return sign * M[-1][-1]


def resultant_xn_plus_a_shifted():
    # h mod (x^13 + 37), using x^13 = -37
    coeff = [0] * n
    for k in range(n):
        coeff[k] += comb(n, k) * (B ** (n - k))
    coeff[0] += C - A

    # Multiplication-by-h matrix in Q[x]/(x^13+37). Its determinant is Res(f,h).
    M = []
    for i in range(n):
        row = []
        for j in range(n):
            val = 0
            for k, c in enumerate(coeff):
                e = j + k
                if e < n:
                    if e == i:
                        val += c
                else:
                    if e - n == i:
                        val -= A * c
            row.append(val)
        M.append(row)
    return abs(bareiss_det(M))


def trim(poly, mod):
    while poly and poly[-1] % mod == 0:
        poly.pop()
    return poly


def poly_divmod(a, b, mod):
    a = trim(a[:], mod)
    b = trim(b[:], mod)
    q = [0] * max(1, len(a) - len(b) + 1)
    while len(a) >= len(b) and b:
        lc = b[-1] % mod
        assert gcd(lc, mod) == 1, "non-unit leading coefficient; split the modulus first"
        coef = a[-1] * pow(lc, -1, mod) % mod
        shift = len(a) - len(b)
        q[shift] = coef
        for i in range(len(b)):
            a[i + shift] = (a[i + shift] - coef * b[i]) % mod
        trim(a, mod)
    return q, a


def find_x():
    N = resultant_xn_plus_a_shifted()

    f = [37] + [0] * 12 + [1]
    h = [0] * 14
    for k in range(14):
        h[k] = comb(13, k) * (42 ** (13 - k))
    h[0] += 42
    f = [c % N for c in f]
    h = [c % N for c in h]

    # Euclidean gcd modulo N. Here it ends as a linear polynomial a0 + a1*x.
    a, b = f, h
    while b:
        _, r = poly_divmod(a, b, N)
        a, b = b, r
    assert len(a) == 2
    x = (-a[0] * pow(a[1], -1, N)) % N
    return x, N


def main():
    x, N = find_x()
    g = gcd(x**13 + 37, (x + 42) ** 13 + 42)
    print(f"x = {x}")
    print(f"g bits = {g.bit_length()}")
    print(f"g == resultant: {g == N}")

    if len(sys.argv) == 3:
        host, port = sys.argv[1], int(sys.argv[2])
        with socket.create_connection((host, port), timeout=10) as s:
            print(s.recv(4096).decode(errors="ignore"), end="")
            s.sendall((str(x) + "\n").encode())
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
            print(data.decode(errors="ignore"))


if __name__ == "__main__":
    main()
