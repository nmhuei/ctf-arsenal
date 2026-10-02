#!/usr/bin/env python3
"""Recover a ternary RLWE secret from the public key advertised by Residuegate."""

import argparse
import json
import math
from pathlib import Path

from fpylll import IntegerMatrix, LLL

Q = 167772161
P = 65537
N = 64


def centered(x: int) -> int:
    x %= Q
    return x - Q if x > Q // 2 else x


def conv_matrix(a: list[int], negacyclic: bool) -> list[list[int]]:
    """Return A such that A @ s is a*s in Z_q[x]/(x^N +/- 1)."""
    matrix = [[0] * N for _ in range(N)]
    for out in range(N):
        for ai, coeff in enumerate(a):
            si = out - ai
            sign = 1
            if si < 0:
                si += N
                if negacyclic:
                    sign = -1
            matrix[out][si] = (sign * coeff) % Q
    return matrix


def matvec(a: list[list[int]], x: list[int]) -> list[int]:
    return [sum(v * xi for v, xi in zip(row, x)) % Q for row in a]


def solve(a: list[int], b: list[int], negacyclic: bool, secret_scale: int, embed: int):
    # p^-1 turns b = A*s + p*e (mod q) into b' = A'*s + e (mod q).
    pinv = pow(P, -1, Q)
    A = conv_matrix(a, negacyclic)
    Ap = [[(pinv * value) % Q for value in row] for row in A]
    bp = [(pinv * value) % Q for value in b]

    # Kannan embedding: a short vector with final coordinate +/-embed carries
    # (secret_scale*s, A'*s-b'+q*z, embed).
    basis = IntegerMatrix(2 * N + 1, 2 * N + 1)
    for i in range(N):
        basis[i, i] = secret_scale
        for j in range(N):
            basis[i, N + j] = Ap[j][i]
    for i in range(N):
        basis[N + i, N + i] = Q
    for j in range(N):
        basis[2 * N, N + j] = -bp[j]
    basis[2 * N, 2 * N] = embed

    LLL.reduction(basis, delta=0.99)
    for r in range(basis.nrows):
        row = [int(basis[r, c]) for c in range(2 * N + 1)]
        if abs(row[-1]) != embed:
            continue
        sign = 1 if row[-1] == embed else -1
        secret = [sign * value // secret_scale for value in row[:N]]
        if any(abs(value) > 8 or (sign * value) % secret_scale for value in row[:N]):
            continue
        product = matvec(A, secret)
        error = [centered((bb - pp) * pinv) for bb, pp in zip(b, product)]
        # Undoing our transform, the original residual must be P*error.
        if all((pp + P * ee - bb) % Q == 0 for pp, ee, bb in zip(product, error, b)):
            return secret, error
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('session_json', type=Path)
    args = parser.parse_args()
    data = json.loads(args.session_json.read_text())
    public = data['crypto']['public_key']
    a = [(-x) % Q for x in public['neg_a']]
    b = public['b']
    for negacyclic in (True, False):
        for secret_scale in (1, 2, 4, 8, 16, 32, 64, 128):
            for embed in (4, 8, 16, 32, 64, 128, 256, 512):
                answer = solve(a, b, negacyclic, secret_scale, embed)
                if answer:
                    secret, error = answer
                    print(json.dumps({
                        'negacyclic': negacyclic,
                        'secret_scale': secret_scale,
                        'embed': embed,
                        'secret': secret,
                        'error': error,
                        'secret_max': max(map(abs, secret)),
                        'error_max': max(map(abs, error)),
                    }))
                    return
    raise SystemExit('No small secret found')


if __name__ == '__main__':
    main()
