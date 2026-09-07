import time
load('test_T_mat.sage')

# Compute the coefficients for Y = (lam^2, lam*mu, mu^2):
# d01 = lam * v1[2] + mu * v2[2]
# d02 = -(lam * v1[1] + mu * v2[1])
# d12 = lam * v1[0] + mu * v2[0]

# Delta01 * Delta02 = r00 * lam^2 + r01 * lam*mu + r02 * mu^2
r00 = - v1[2] * v1[1]
r01 = - (v1[2] * v2[1] + v2[2] * v1[1])
r02 = - v2[2] * v2[1]

# Delta01 * Delta12
r10 = v1[2] * v1[0]
r11 = v1[2] * v2[0] + v2[2] * v1[0]
r12 = v2[2] * v2[0]

# Delta02 * Delta12
r20 = - v1[1] * v1[0]
r21 = - (v1[1] * v2[0] + v2[1] * v1[0])
r22 = - v2[1] * v2[0]

# Multipliers:
# A0 = - n * (h1*h2)^-1 * (Delta01 * Delta02) mod h0
inv_h1h2 = pow(int(h1 * h2), -1, h0)
C0 = (- n * inv_h1h2) % h0

inv_h0h2 = pow(int(h0 * h2), -1, h1)
C1 = (n * inv_h0h2) % h1

inv_h0h1 = pow(int(h0 * h1), -1, h2)
C2 = (- n * inv_h0h1) % h2

row0 = [(C0 * x) % h0 for x in [r00, r01, r02]]
row1 = [(C1 * x) % h1 for x in [r10, r11, r12]]
row2 = [(C2 * x) % h2 for x in [r20, r21, r22]]

print("Coefficients setup complete.")

# Variable bounds:
# |lam| <= 2^286, |mu| <= 2^286 => Y <= 2^572
# A_i <= 2^1248
# Target size for both: 2^1248
# Weight on Y: W_Y = 2^(1248 - 572) = 2^676
# Weight on A: 1

W_Y = 1 << (1248 - 572)
print("W_Y bit length:", W_Y.bit_length())

# Lattice matrix 6x6:
# Rows:
# 3 rows from Y:
# (row0[j], row1[j], row2[j], W_Y * delta_{j, k})
# 3 rows from moduli:
# (h0, 0, 0, 0, 0, 0)
# (0, h1, 0, 0, 0, 0)
# (0, 0, h2, 0, 0, 0)

M = Matrix(ZZ, 6, 6)
for j in range(3):
    M[j, 0] = row0[j]
    M[j, 1] = row1[j]
    M[j, 2] = row2[j]
    M[j, 3 + j] = W_Y

M[3, 0] = h0
M[4, 1] = h1
M[5, 2] = h2

print(f"Matrix determinant bit length: {M.det().bit_length()}")
print(f"Minkowski bound: {M.det().bit_length() / 6:.1f} bits")

print("[*] Running LLL on 6x6...")
t0 = time.time()
L_red = M.LLL()
print(f"[+] LLL done in {time.time() - t0:.3f}s!")

for idx, r in enumerate(L_red.rows()):
    norm_bits = vector(r).norm().n().log(2)
    A_cand = [abs(r[j]) for j in range(3)]
    Y_cand = [abs(r[3 + j]) // W_Y for j in range(3)]
    print(f"Row {idx}: norm bits = {norm_bits:.1f}")
    print(f"  A bits: {[x.bit_length() for x in A_cand]}")
    print(f"  Y bits: {[x.bit_length() for x in Y_cand]}")
    # Check rank-1:
    y0 = r[3] // W_Y
    y1 = r[4] // W_Y
    y2 = r[5] // W_Y
    if y0 * y2 == y1^2 and (y0 != 0 or y1 != 0 or y2 != 0):
        print(f"  [!] RANK-1 FOUND! y = ({y0}, {y1}, {y2})")

# Also run BKZ with block size 10..20:
print("\n[*] Running BKZ(block_size=10)...")
L_bkz = M.BKZ(block_size=10)
for idx, r in enumerate(L_bkz.rows()[:3]):
    norm_bits = vector(r).norm().n().log(2)
    A_cand = [abs(r[j]) for j in range(3)]
    Y_cand = [abs(r[3 + j]) // W_Y for j in range(3)]
    print(f"BKZ Row {idx}: norm bits = {norm_bits:.1f}")
    print(f"  A bits: {[x.bit_length() for x in A_cand]}")
    print(f"  Y bits: {[x.bit_length() for x in Y_cand]}")
    y0 = r[3] // W_Y
    y1 = r[4] // W_Y
    y2 = r[5] // W_Y
    if y0 * y2 == y1^2 and (y0 != 0 or y1 != 0 or y2 != 0):
        print(f"  [!] RANK-1 FOUND! y = ({y0}, {y1}, {y2})")
