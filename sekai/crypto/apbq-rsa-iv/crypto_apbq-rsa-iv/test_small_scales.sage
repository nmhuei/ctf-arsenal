load('test_factor_s.sage')

# w_int is the integer vector:
print("w_int:", w_int)

# Let's test w = w_int / denom for various integer multipliers/divisors:
for mul in range(1, 20):
    for div in range(1, 20):
        # candidate w:
        w_cand = [w_int[0] * mul / div, w_int[1] * mul / div, w_int[2] * mul / div]
        
        # Test norm of w_cand . L vs H:
        # D_j^2 = H_j^2 - 4 n A_j => H_j^2 - D_j^2 = 0 mod n!
        wL0 = w_cand[0]*L[0, 0] + w_cand[1]*L[1, 0] + w_cand[2]*L[2, 0]
        val = H[0]^2 - wL0^2
        g = gcd(ZZ(round(val)), n)
        if 1 < g < n:
            print(f"[!] SUCCESS via norm relation! mul={mul}, div={div}, g={g}")
            exit(0)
        
        # Test J(w_cand) mod n:
        # J_cand = (ks[0]*w_cand[0] + ks[1]*w_cand[1] + ks[2]*w_cand[2]) mod n
        J_val = (ks[0]*w_cand[0] + ks[1]*w_cand[1] + ks[2]*w_cand[2])
        if J_val.denominator() == 1:
            J_int = ZZ(J_val) % n
            for diff in [1, -1]:
                g = gcd(J_int + diff, n)
                if 1 < g < n:
                    print(f"[!] SUCCESS via J(w)! mul={mul}, div={div}, g={g}")
                    exit(0)

print("Finished testing small scales 1..20")
