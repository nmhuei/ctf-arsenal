#!/usr/bin/env python3
import re
import os
import hashlib
import gmpy2
from gmpy2 import mpz

SOLVER_DIR = os.path.dirname(os.path.abspath(__file__))
CHALL_PATH = os.path.join(SOLVER_DIR, "..", "challenge", "chall.sage")

def solve():
    print("[*] Reading challenge parameters from chall.sage...")
    with open(CHALL_PATH) as f:
        content = f.read()

    n_match = re.search(r"# N = (\d+)", content)
    e_match = re.search(r"# e = (\d+)", content)
    c_match = re.search(r"# c = (.*)", content)

    N = mpz(n_match.group(1))
    e = mpz(e_match.group(1))
    c_str = c_match.group(1).strip()
    n = 10
    N10 = N**n

    print("[*] Performing Generalized Wiener Attack on e / N^10...")
    def continued_fraction(num, den):
        while den != 0:
            q = num // den
            yield q
            num, den = den, num - q * den

    def convergents(cf):
        p0, q0 = mpz(0), mpz(1)
        p1, q1 = mpz(1), mpz(0)
        for a in cf:
            p2 = a * p1 + p0
            q2 = a * q1 + q0
            yield p2, q2
            p0, q0 = p1, q1
            p1, q1 = p2, q2

    p, q = None, None
    for idx, (k, d) in enumerate(convergents(continued_fraction(e, N10))):
        if k == 0: continue
        if (e * d + 1) % k == 0:
            phi_cand = (e * d + 1) // k
            S = N10 - phi_cand + 1
            P = N10
            disc = S**2 - 4*P
            if disc >= 0:
                sqrt_disc, exact = gmpy2.isqrt_rem(disc)
                if exact == 0:
                    p10 = (S + sqrt_disc) // 2
                    q10 = (S - sqrt_disc) // 2
                    p_root, exact_p = gmpy2.iroot(p10, 10)
                    q_root, exact_q = gmpy2.iroot(q10, 10)
                    if exact_p and exact_q and p_root * q_root == N:
                        p, q = p_root, q_root
                        print(f"[+] Successfully factored N at convergent #{idx}!")
                        break

    assert p is not None and q is not None, "Failed to factor N"

    print("[*] Computing quotient ring group exponent lambda(N)...")
    # In F_p[t]/(t^10 - 2), 2 is a square but not 5th power -> degree 5 irreducible factors
    # In F_q[t]/(t^10 - 2), 2 is a square, 5th roots of unity have degree 4 -> degree 4 irreducible factors
    lambda_p = p**5 - 1
    lambda_q = q**4 - 1
    lambda_N = (lambda_p * lambda_q) // gmpy2.gcd(lambda_p, lambda_q)

    d_true = gmpy2.invert(e, lambda_N)
    print(f"[+] Decryption exponent d_true computed ({d_true.bit_length()} bits).")

    # Parse c polynomial coeffs in ascending order t^0 .. t^9
    coeffs = [mpz(0)] * 10
    terms = c_str.split("+")
    for term in terms:
        term = term.strip()
        if "*t^" in term:
            coef, power = term.split("*t^")
            coeffs[int(power)] = mpz(coef.strip())
        elif "*t" in term:
            coef, _ = term.split("*t")
            coeffs[1] = mpz(coef.strip())
        else:
            coeffs[0] = mpz(term.strip())

    def poly_mul(p1, p2, N):
        res = [mpz(0)] * 19
        for i in range(10):
            for j in range(10):
                res[i + j] = (res[i + j] + p1[i] * p2[j]) % N
        out = [mpz(0)] * 10
        for k in range(10):
            out[k] = res[k]
        for k in range(10, 19):
            out[k - 10] = (out[k - 10] + 2 * res[k]) % N
        return out

    def poly_pow(base, exp, N):
        res = [mpz(0)] * 10
        res[0] = mpz(1)
        cur = base[:]
        while exp > 0:
            if exp & 1:
                res = poly_mul(res, cur, N)
            cur = poly_mul(cur, cur, N)
            exp >>= 1
        return res

    print("[*] Decrypting ciphertext c^d_true mod (t^10 - 2, N)...")
    dec_poly = poly_pow(coeffs, d_true, N)

    max_bytes = max((int(x).bit_length() + 7) // 8 for x in dec_poly)
    chunks = [int(x).to_bytes(max_bytes, "big") for x in dec_poly]
    flag_padded = b"".join(chunks)
    pad_len = flag_padded[-1]
    raw_flag = flag_padded[:-pad_len]
    print(f"[+] Raw decrypted flag: {raw_flag.decode()}")

    # Generate candidate flag representations
    inner_raw = raw_flag[9:-1] # inner string: c0ngr4tzzz_h3ngk3rrrr_g3n3r4l1Zed_w13n3R_4ttacK
    h_inner = hashlib.sha256(inner_raw).hexdigest()[:16]
    
    flag_compfest = f"COMPFEST{{{inner_raw.decode()}_{h_inner}}}"
    flag_compfest18 = f"COMPFEST18{{{inner_raw.decode()}_{h_inner}}}"

    print("\n" + "="*70)
    print(f"[🏁] PRIMARY FLAG: {flag_compfest}")
    print(f"[*] Alternative (COMPFEST18 prefix): {flag_compfest18}")
    print(f"[*] Raw Decrypted: {raw_flag.decode()}")
    print("="*70)
    return flag_compfest

if __name__ == "__main__":
    solve()
