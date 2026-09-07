load('test_solve_5vars.sage')

r0 = vector(ZZ, [L_red.rows()[0][1 + i] // weights[i] for i in range(5)])
r1 = vector(ZZ, [L_red.rows()[1][1 + i] // weights[i] for i in range(5)])

print("r0:", r0)
print("r1:", r1)

# x(a, b) = a * r0 + b * r1
# indices: 0: x1, 1: x2, 2: x3, 3: x4, 4: x5
# x1 * x2 = x5^2:
# (a * r0[0] + b * r1[0]) * (a * r0[1] + b * r1[1]) - (a * r0[4] + b * r1[4])^2 = 0

C_aa = r0[0] * r0[1] - r0[4]^2
C_ab = r0[0] * r1[1] + r0[1] * r1[0] - 2 * r0[4] * r1[4]
C_bb = r1[0] * r1[1] - r1[4]^2

print(f"Quadratic: {C_aa} * a^2 + {C_ab} * a * b + {C_bb} * b^2 = 0")

disc = C_ab^2 - 4 * C_aa * C_bb
print("Discriminant bit length:", disc.bit_length())
print("Is disc a square?:", disc.is_square())

if disc >= 0 and disc.is_square():
    s_disc = ZZ(isqrt(disc))
    # Roots for a/b:
    # 2 * C_aa * a + (C_ab +- s_disc) * b = 0
    # b = 2 * C_aa, a = -(C_ab +- s_disc)
    cand_pairs = [
        (-(C_ab + s_disc), 2 * C_aa),
        (-(C_ab - s_disc), 2 * C_aa)
    ]
    
    for a_val, b_val in cand_pairs:
        g = gcd(a_val, b_val)
        a_val //= g
        b_val //= g
        print(f"\n[*] Testing candidate (a, b) = ({a_val}, {b_val})")
        
        x_sol = a_val * r0 + b_val * r1
        print("x_sol:", x_sol)
        
        x1_val, x2_val, x3_val, x4_val, x5_val = x_sol
        for sign in [1, -1]:
            x1 = sign * x1_val
            x2 = sign * x2_val
            x3 = sign * x3_val
            x4 = sign * x4_val
            x5 = sign * x5_val
            
            if x1 >= 0 and x2 >= 0 and x1.is_square() and x2.is_square():
                w1 = ZZ(isqrt(x1))
                w2 = ZZ(isqrt(x2))
                print(f"[+] Found square roots! w1 = {w1}, w2 = {w2}")
                if w1 > 0:
                    w0 = x3 // w1
                    for s0 in [1, -1]:
                        for s1 in [1, -1]:
                            for s2 in [1, -1]:
                                w_test = (s0 * w0, s1 * w1, s2 * w2)
                                J = (ks[0]*w_test[0] + ks[1]*w_test[1] + ks[2]*w_test[2]) % n
                                p_cand = gcd(J - 1, n)
                                if 1 < p_cand < n:
                                    q_cand = n // p_cand
                                    print("\n" + "="*50)
                                    print(f"[!] SUCCESS! Factored n!")
                                    print(f"p = {p_cand}")
                                    print(f"q = {q_cand}")
                                    phi = (p_cand - 1) * (q_cand - 1)
                                    d = pow(e, -1, phi)
                                    pt = pow(ct, d, n)
                                    flag = long_to_bytes(pt)
                                    print(f"[FLAG] {flag.decode()}")
                                    with open('FLAG.txt', 'w') as out_f:
                                        out_f.write(flag.decode() + '\n')
                                    print("="*50)
                                    exit(0)
