#!/usr/bin/env python3
# Solve Lack of Entropy (Firebird Internal CTF)
# q is int(base3_digits(p)) so p=B(3), q=B(10) for the same digit polynomial B with coefficients in {0,1,2}.

from pathlib import Path
import re

OUT = Path(__file__).parent / "files" / "output_6dab4505a9ec7cd150ae7d3d6321bffc.txt"

def parse_output(path=OUT):
    txt = Path(path).read_text()
    vals = {}
    for name in ("n", "e", "c"):
        m = re.search(rf"{name}\s*=\s*(\d+)", txt)
        if not m:
            raise ValueError(f"missing {name} in {path}")
        vals[name] = int(m.group(1))
    return vals["n"], vals["e"], vals["c"]

def possible_lengths(n):
    # L = number of ternary digits of p = number of decimal digits of q.
    ans = []
    pow3 = 1
    for L in range(1, 1000):
        # p in [3^(L-1), 3^L-1]
        # q has L decimal digits using only 0,1,2 and msd !=0:
        # q in [10^(L-1), 222...222]
        pmin = 3 ** (L - 1)
        pmax = 3 ** L - 1
        qmin = 10 ** (L - 1)
        qmax = 2 * (10 ** L - 1) // 9
        if pmin * qmin <= n <= pmax * qmax:
            ans.append(L)
        if pmin * qmin > n and L > 1:
            break
    return ans

def factor_special(n):
    """Recover p,q from n where q is decimal reading of base-3 digits of p."""
    for L in possible_lengths(n):
        pow3 = [1] * (L + 1)
        pow10 = [1] * (L + 1)
        for i in range(1, L + 1):
            pow3[i] = pow3[i - 1] * 3
            pow10[i] = pow10[i - 1] * 10
        max_dec_low = [2 * (pow10[k] - 1) // 9 for k in range(L + 1)]

        # DFS from the most significant shared digit downward.
        # P_hi/Q_hi are already-built prefixes interpreted in base 3/base 10.
        stack = [(L - 1, 0, 0)]
        while stack:
            pos, P_hi, Q_hi = stack.pop()
            if pos < 0:
                p, q = P_hi, Q_hi
                if p * q == n:
                    return p, q
                continue

            remaining = pos
            digits = (1, 2) if pos == L - 1 else (0, 1, 2)
            for a in digits:
                P2 = P_hi * 3 + a
                Q2 = Q_hi * 10 + a

                # Unknown lower digits produce bounded intervals.
                p_min = P2 * pow3[remaining]
                p_max = p_min + (pow3[remaining] - 1)
                q_min = Q2 * pow10[remaining]
                q_max = q_min + max_dec_low[remaining]

                if p_min * q_min <= n <= p_max * q_max:
                    stack.append((pos - 1, P2, Q2))
    raise ValueError("factor not found")

def main():
    n, e, c = parse_output()
    p, q = factor_special(n)
    assert p * q == n
    assert int(format(p, "b"), 2) == p  # harmless sanity line: p is an int
    assert int("".join(str(x) for x in []), 10) if False else True
    # Real relation check: q is the base-3 representation of p, read as decimal.
    tmp = p
    digs = []
    while tmp:
        digs.append(str(tmp % 3))
        tmp //= 3
    assert int("".join(reversed(digs))) == q

    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    m = pow(c, d, n)
    flag = m.to_bytes((m.bit_length() + 7) // 8, "big")

    print(f"p = {p}")
    print(f"q = {q}")
    print(flag.decode())

if __name__ == "__main__":
    main()
