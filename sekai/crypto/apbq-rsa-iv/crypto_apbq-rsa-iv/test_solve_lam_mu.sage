load('test_lam_mu_modn.sage')

# R is ratio0:
R_val = ratio0

# 2x2 lattice:
# [n, 0]
# [R_val, 1]
M_2 = Matrix(ZZ, [
    [n, 0],
    [R_val, 1]
])

print("Running LLL on 2x2 lattice...")
L_2 = M_2.LLL()
print("L_2 rows:")
for idx, r in enumerate(L_2.rows()):
    print(f"Row {idx}: norm bits = {vector(r).norm().n().log(2):.1f}")
    print(f"  entry 0 (mu * R - k*n): {r[0].bit_length()} bits, entry 1 (mu): {r[1].bit_length()} bits")
    print(f"  vector: {r}")

# Check continued fraction of R_val / n:
cf = continued_fraction(R_val / n)
print("\nChecking convergents of R_val / n:")
for conv in cf.convergents():
    p_c, q_c = conv.numerator(), conv.denominator()
    diff = abs(R_val * q_c - p_c * n)
    if q_c.bit_length() > 400 and q_c.bit_length() < 500:
        print(f"Convergent: q_c bits = {q_c.bit_length()}, diff bits = {diff.bit_length()}")
        lam_cand = diff
        mu_cand = q_c
        print(f"  lam = {lam_cand}, mu = {mu_cand}")
