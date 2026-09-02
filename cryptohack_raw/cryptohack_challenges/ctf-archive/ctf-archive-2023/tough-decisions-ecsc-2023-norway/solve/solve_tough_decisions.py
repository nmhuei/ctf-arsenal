#!/usr/bin/env python3
import ast
import sys
from pathlib import Path


def load_groups(path: str):
    lines = Path(path).read_text().splitlines()
    return [ast.literal_eval(line) for line in lines if line.strip()]


def parity_mask(a: bytes) -> int:
    mask = 0
    for i, x in enumerate(a):
        if x & 1:
            mask |= 1 << i
    return mask


def solve(path: str):
    groups = []
    for grp in load_groups(path):
        eqs = []
        for a, y in grp:
            eqs.append((parity_mask(a), y & 1))
        groups.append(eqs)

    best_score = -1
    best_s = None
    best_hist = None

    # Secret parity is only 16 bits, so brute force all possibilities over GF(2).
    for s in range(1 << 16):
        hist = [0] * 7
        score = 0
        for eqs in groups:
            ok = 0
            for mask, rhs in eqs:
                if ((mask & s).bit_count() & 1) == rhs:
                    ok += 1
            hist[ok] += 1
            if ok == 6:
                score += 1
        if score > best_score:
            best_score = score
            best_s = s
            best_hist = hist

    bits = []
    for eqs in groups:
        ok = sum((((mask & best_s).bit_count() & 1) == rhs) for mask, rhs in eqs)
        # real sample => flag bit 0; fake sample => flag bit 1
        bits.append(0 if ok == 6 else 1)

    flag = bytearray()
    for i in range(0, len(bits), 8):
        flag.append(sum(bits[i + j] << j for j in range(8) if i + j < len(bits)))

    return best_s, best_score, best_hist, bytes(flag)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} output.txt")
        raise SystemExit(1)
    s, score, hist, flag = solve(sys.argv[1])
    print(f"secret parity = {s:#06x}")
    print(f"real groups    = {score}")
    print(f"match histogram= {hist}")
    print(flag.decode())
