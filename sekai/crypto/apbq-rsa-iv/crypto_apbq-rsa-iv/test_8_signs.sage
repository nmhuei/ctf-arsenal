load('test_sol2_w0.sage')

# w0_cand, w1_cand, w2_cand:
w0_base = w0_from_x3
w1_base = QQ(w1)
w2_base = QQ(w2)

print("w0_base:", w0_base)
print("w1_base:", w1_base)
print("w2_base:", w2_base)

# Test candidate w vectors:
for s0 in [1, -1]:
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            for scale in [1, 1/2, 2, 1/4, 4]:
                w_cand = vector(QQ, [s0 * w0_base * scale, s1 * w1_base * scale, s2 * w2_base * scale])
                
                # u = (c + w) / 2
                u = (c + w_cand) / 2
                pa_cand = u * L
                
                for coord in pa_cand:
                    if coord.denominator() == 1:
                        g = gcd(ZZ(coord), n)
                        if 1 < g < n:
                            print(f"[!] SUCCESS! Factored n! p = {g}")
                            q_val = n // g
                            print(f"p = {g}")
                            print(f"q = {q_val}")
                            exit(0)
                
                # Also test gcd((w . L)_j^2 - H_j^2, n):
                wL = w_cand * L
                for j in range(3):
                    diff = H[j]^2 - wL[j]^2
                    if diff.denominator() == 1:
                        g = gcd(ZZ(diff), n)
                        if 1 < g < n:
                            print(f"[!] SUCCESS via diff! Factored n! p = {g}")
                            exit(0)

print("Finished 8 signs test")
