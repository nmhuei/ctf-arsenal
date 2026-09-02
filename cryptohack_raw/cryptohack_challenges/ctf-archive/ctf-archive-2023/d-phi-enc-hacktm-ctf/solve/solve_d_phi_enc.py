#!/usr/bin/env python3
from math import isqrt
from pathlib import Path

# Parse output.txt style file (or use default path next to this script / current dir)
def parse_output(path):
    vals = {}
    for line in Path(path).read_text().splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            vals[k.strip()] = int(v.strip())
    return vals['n'], vals['enc_d'], vals['enc_phi'], vals['enc_flag']


def solve(n, enc_d, enc_phi, enc_flag):
    e = 3

    # getStrongPrime(..., e=3) gives p,q != 1 mod 3, so phi == 1 mod 3.
    # Hence d = inverse(3, phi) = (2*phi + 1) / 3.
    # Let s = p + q, phi = n - s + 1 == 1 - s (mod n).
    # 27*enc_d - 8*enc_phi == (2phi+1)^3 - 8phi^3
    #                         == 12phi^2 + 6phi + 1
    #                         == 12s^2 - 30s + 19   (mod n).
    A = (27 * enc_d - 8 * enc_phi) % n

    # Since p and q are both 1024-bit, s^2 is close to 4n, so k is small.
    for k in range(256):
        C = A + k * n
        # 12*s^2 - 30*s + 19 = C
        # discriminant = (-30)^2 - 4*12*(19-C) = 48*C - 12
        D = 48 * C - 12
        r = isqrt(D)
        if r * r != D:
            continue
        if (30 + r) % 24 != 0:
            continue
        s = (30 + r) // 24

        # factor n using s = p+q
        delta = s * s - 4 * n
        rd = isqrt(delta)
        if rd * rd != delta:
            continue
        p = (s - rd) // 2
        q = (s + rd) // 2
        if p * q != n:
            continue

        phi = (p - 1) * (q - 1)
        d = pow(e, -1, phi)
        m = pow(enc_flag, d, n)
        return m.to_bytes((m.bit_length() + 7) // 8, 'big'), p, q, k

    raise ValueError('failed to recover p, q; increase k bound')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        output_path = '../files/output_390a72a8ed392b4899a9a7fa7a6d04ea.txt'
    n, enc_d, enc_phi, enc_flag = parse_output(output_path)
    flag, p, q, k = solve(n, enc_d, enc_phi, enc_flag)
    print(f'[+] k = {k}')
    print(f'[+] p bits = {p.bit_length()}, q bits = {q.bit_length()}')
    print(flag.decode())
