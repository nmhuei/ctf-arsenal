load('test_clean_50_toy.sage')

# P_raw = (ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1
# P1_raw = (w0*L[0, 0] + w1*L[1, 0] + w2*L[2, 0])^2 - H[0]^2
# P2_raw = (w0*L[0, 1] + w1*L[1, 1] + w2*L[2, 1])^2 - H[1]^2
# P3_raw = (w0*L[0, 2] + w1*L[1, 2] + w2*L[2, 2])^2 - H[2]^2

R_poly.<w0, w1, w2> = ZZ[]
P_raw = (ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1
P1_raw = (w0*L[0, 0] + w1*L[1, 0] + w2*L[2, 0])^2 - H[0]^2
P2_raw = (w0*L[0, 1] + w1*L[1, 1] + w2*L[2, 1])^2 - H[1]^2
P3_raw = (w0*L[0, 2] + w1*L[1, 2] + w2*L[2, 2])^2 - H[2]^2

# Difference mod n:
diff1 = P1_raw - H[0]^2 * P_raw
diff2 = P2_raw - H[1]^2 * P_raw
diff3 = P3_raw - H[2]^2 * P_raw

# Check all coefficients of diff1, diff2, diff3 are divisible by n:
print("diff1 % n == 0:", all(c % n == 0 for c in diff1.coefficients()))
print("diff2 % n == 0:", all(c % n == 0 for c in diff2.coefficients()))
print("diff3 % n == 0:", all(c % n == 0 for c in diff3.coefficients()))

R1 = sum((c // n) * m for c, m in zip(diff1.coefficients(), diff1.monomials()))
R2 = sum((c // n) * m for c, m in zip(diff2.coefficients(), diff2.monomials()))
R3 = sum((c // n) * m for c, m in zip(diff3.coefficients(), diff3.monomials()))

print("R1(w):", R1(w[0], w[1], w[2]))
print("R2(w):", R2(w[0], w[1], w[2]))
print("R3(w):", R3(w[0], w[1], w[2]))

# Ideal over QQ:
R_qq.<w0, w1, w2> = QQ[]
I1 = ideal([R_qq(P), R_qq(R1)])
print("Ideal(P, R1) dimension:", I1.dimension())
I2 = ideal([R_qq(P), R_qq(R1), R_qq(R2)])
print("Ideal(P, R1, R2) dimension:", I2.dimension())
I3 = ideal([R_qq(P), R_qq(R1), R_qq(R2), R_qq(R3)])
print("Ideal(P, R1, R2, R3) dimension:", I3.dimension())
