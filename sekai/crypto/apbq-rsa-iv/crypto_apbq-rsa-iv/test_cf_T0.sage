load('test_get_A.sage')

cf = continued_fraction(T0 / h0)
print("Number of partial quotients:", len(cf))

# Print convergents where denominator <= 2^100:
for idx, conv in enumerate(cf.convergents()):
    q_den = conv.denominator()
    p_num = conv.numerator()
    if q_den.bit_length() > 200:
        break
    
    # Residue:
    # a * T0 - q0 * h0:
    res = (p_num * h0 - q_den * T0)
    res_mod = (q_den * T0) % h0
    if res_mod.bit_length() < 1300:
        print(f"Convergent {idx}: num = {p_num}, den = {q_den}")
        print(f"  res_mod bit length: {res_mod.bit_length()}")
        
        # Test if this gives flag:
        # A0 = res_mod // (q_den * S^2)
        # S0^2 = H0^2 - 4*n*A0
        diff = H[0]^2 - 4 * n * res_mod
        if diff >= 0 and diff.is_square():
            S0 = ZZ(isqrt(diff))
            g = gcd(H[0] + S0, n)
            if 1 < g < n:
                print(f"[!] SUCCESS! Factored n! p = {g}")
                exit(0)

print("Finished checking T0 continued fractions")
