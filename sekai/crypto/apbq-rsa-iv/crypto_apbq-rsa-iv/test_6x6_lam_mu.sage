import time
load('test_lam_mu_system.sage')

# System:
# row0 = [r00, r01, r02] mod h0
# row1 = [r10, r11, r12] mod h1
# row2 = [r20, r21, r22] mod h2

# Bounds:
# Y = (lam^2, lam*mu, mu^2) <= 2^850
# A = (A0, A1, A2) <= 2^1248

W_Y = 1 << 850
W_A = 1 << 1248

# We want the vector:
# (A0 * scale_A, A1 * scale_A, A2 * scale_A, lam^2 * scale_Y, lam*mu * scale_Y, mu^2 * scale_Y)
# to have equalized components!
# So scale_A = 1 << 850
# scale_Y = 1 << 1248
# Target component size: 850 + 1248 = 2098 bits.

scale_A = 1 << 850
scale_Y = 1 << 1248

M_lat = Matrix(ZZ, 6, 6)

# Rows from Y components:
for j in range(3):
    M_lat[j, 0] = row0[j] * scale_A
    M_lat[j, 1] = row1[j] * scale_A
    M_lat[j, 2] = row2[j] * scale_A
    M_lat[j, 3 + j] = scale_Y

# Rows from moduli:
M_lat[3, 0] = h0 * scale_A
M_lat[4, 1] = h1 * scale_A
M_lat[5, 2] = h2 * scale_A

print("Running LLL on 6x6 lattice...")
t0 = time.time()
L_red = M_lat.LLL()
print(f"LLL completed in {time.time() - t0:.3f}s!")

for idx, r in enumerate(L_red.rows()):
    norm_bits = vector(r).norm().n().log(2)
    # Extract candidate Y:
    Y_cand = [r[3 + j] // scale_Y for j in range(3)]
    A_cand = [r[j] // scale_A for j in range(3)]
    print(f"Row {idx}: norm bits = {norm_bits:.1f}")
    print(f"  Y_cand bits: {[abs(x).bit_length() for x in Y_cand]}")
    print(f"  A_cand bits: {[abs(x).bit_length() for x in A_cand]}")
    # Check if Y_cand[0] * Y_cand[2] == Y_cand[1]^2:
    if Y_cand[0] != 0 and Y_cand[2] != 0:
        is_rank1 = (Y_cand[0] * Y_cand[2] == Y_cand[1]^2)
        print(f"  Is rank-1 (lam^2 * mu^2 == (lam*mu)^2): {is_rank1}")
        if is_rank1:
            print("[!] FOUND RANK-1 RELATION!")
            # lam, mu:
            if Y_cand[0] > 0 and Y_cand[2] > 0:
                lam_val = isqrt(Y_cand[0])
                mu_val = isqrt(Y_cand[2])
                print(f"  lam = {lam_val}, mu = {mu_val}")
