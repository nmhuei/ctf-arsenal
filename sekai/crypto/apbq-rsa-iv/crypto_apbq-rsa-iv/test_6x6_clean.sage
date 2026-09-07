import time

with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints
h = vector(ZZ, hints)

# Kernel of h over ZZ:
M_h = Matrix(ZZ, [hints])
ker_h = M_h.right_kernel()
B_ker = ker_h.basis_matrix().LLL()
v1, v2 = B_ker.rows()
if vector(v1).cross_product(vector(v2)) != h:
    if vector(v1).cross_product(vector(v2)) == -h:
        v2 = -v2

print("v1 norm bits:", vector(QQ, v1).norm().n().log(2))
print("v2 norm bits:", vector(QQ, v2).norm().n().log(2))

# Monomial coefficients in Delta01 * Delta02, etc.
# d01 = lam * v1[2] + mu * v2[2]
# d02 = -(lam * v1[1] + mu * v2[1])
# d12 = lam * v1[0] + mu * v2[0]

r00 = - v1[2] * v1[1]
r01 = - (v1[2] * v2[1] + v2[2] * v1[1])
r02 = - v2[2] * v2[1]

r10 = v1[2] * v1[0]
r11 = v1[2] * v2[0] + v2[2] * v1[0]
r12 = v2[2] * v2[0]

r20 = - v1[1] * v1[0]
r21 = - (v1[1] * v2[0] + v2[1] * v1[0])
r22 = - v2[1] * v2[0]

inv_h1h2 = pow(int(h1 * h2), -1, h0)
C0 = (- n * inv_h1h2) % h0

inv_h0h2 = pow(int(h0 * h2), -1, h1)
C1 = (n * inv_h0h2) % h1

inv_h0h1 = pow(int(h0 * h1), -1, h2)
C2 = (- n * inv_h0h1) % h2

row0 = [(C0 * x) % h0 for x in [r00, r01, r02]]
row1 = [(C1 * x) % h1 for x in [r10, r11, r12]]
row2 = [(C2 * x) % h2 for x in [r20, r21, r22]]

# Weight:
# Y = (lam^2, lam*mu, mu^2) <= 2^572
# Target norm: 2^1248
W_Y = 1 << (1248 - 572)

M = Matrix(ZZ, 6, 6)
for j in range(3):
    M[j, 0] = row0[j]
    M[j, 1] = row1[j]
    M[j, 2] = row2[j]
    M[j, 3 + j] = W_Y

M[3, 0] = h0
M[4, 1] = h1
M[5, 2] = h2

print(f"Matrix det bit length: {M.det().bit_length()}")
print(f"Minkowski bound: {float(M.det().bit_length() / 6):.1f} bits")

print("[*] Running LLL on 6x6...")
t0 = time.time()
L_red = M.LLL()
print(f"[+] LLL completed in {time.time() - t0:.3f}s!")

for idx, r in enumerate(L_red.rows()):
    norm_bits = vector(r).norm().n().log(2)
    A_cand = [abs(r[j]) for j in range(3)]
    Y_cand = [abs(r[3 + j]) // W_Y for j in range(3)]
    print(f"Row {idx}: norm bits = {norm_bits:.1f}")
    print(f"  A bits: {[x.bit_length() for x in A_cand]}")
    print(f"  Y bits: {[x.bit_length() for x in Y_cand]}")
    y0 = r[3] // W_Y
    y1 = r[4] // W_Y
    y2 = r[5] // W_Y
    if y0 * y2 == y1^2 and (y0 != 0 or y1 != 0 or y2 != 0):
        print(f"  [!] RANK-1 FOUND! y = ({y0}, {y1}, {y2})")

print("\n[*] Running BKZ(block_size=15)...")
L_bkz = M.BKZ(block_size=15)
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
