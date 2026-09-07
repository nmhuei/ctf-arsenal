with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h = vector(ZZ, hints)
M = Matrix(ZZ, [[hints[0], hints[1], hints[2]], [n, 0, 0], [0, n, 0], [0, 0, n]])
L = Matrix(ZZ, [r for r in M.hermite_form().rows() if vector(r).norm() > 0]).LLL()

ker_h = Matrix(ZZ, [hints]).right_kernel().basis_matrix().LLL()
v1, v2 = ker_h[0], ker_h[1]
if v1.cross_product(v2) != vector(ZZ, hints):
    if v1.cross_product(v2) == -vector(ZZ, hints):
        v2 = -v2

# Determinant linear forms:
# Delta01 = lam * v1[2] + mu * v2[2]
# Delta02 = -(lam * v1[1] + mu * v2[1])
# Delta12 = lam * v1[0] + mu * v2[0]
# Square forms in u=lam^2, v=lam*mu, w=mu^2:
R01, S01 = v1[2], v2[2]
R02, S02 = -v1[1], -v2[1]
R12, S12 = v1[0], v2[0]

q_D01 = (R01^2, 2*R01*S01, S01^2)
q_D02 = (R02^2, 2*R02*S02, S02^2)

# Residue rows:
# A0 = -n * (h1^2)^-1 * Delta01^2 mod h0
# A1 = -n * (h0^2)^-1 * Delta01^2 mod h1
# A2 = -n * (h0^2)^-1 * Delta02^2 mod h2

inv_h1_sq_mod_h0 = pow(int(h[1]), -2, h[0])
inv_h0_sq_mod_h1 = pow(int(h[0]), -2, h[1])
inv_h0_sq_mod_h2 = pow(int(h[0]), -2, h[2])

scale0 = (-n * inv_h1_sq_mod_h0) % h[0]
scale1 = (-n * inv_h0_sq_mod_h1) % h[1]
scale2 = (-n * inv_h0_sq_mod_h2) % h[2]

row0 = [(scale0 * c) % h[0] for c in q_D01]
row1 = [(scale1 * c) % h[1] for c in q_D01]
row2 = [(scale2 * c) % h[2] for c in q_D02]

print("Residue row 0 mod h0:", [x.bit_length() for x in row0])
print("Residue row 1 mod h1:", [x.bit_length() for x in row1])
print("Residue row 2 mod h2:", [x.bit_length() for x in row2])

# Unknown bounds:
# u, v, w <= 2^570
# A0, A1, A2 <= 2^1248
W = 1 << (1248 - 570)
print("Weight W bit length:", W.bit_length())

# Lattice matrix in 6D:
# Vector (u, v, w, -k0, -k1, -k2) * Mat =
# (W*u, W*v, W*w, A0, A1, A2)
Mat = Matrix(ZZ, [
    [W, 0, 0, row0[0], row1[0], row2[0]],
    [0, W, 0, row0[1], row1[1], row2[1]],
    [0, 0, W, row0[2], row1[2], row2[2]],
    [0, 0, 0, h[0], 0, 0],
    [0, 0, 0, 0, h[1], 0],
    [0, 0, 0, 0, 0, h[2]],
])

print("Lattice determinant bit length:", Mat.determinant().abs().n().log(2))
print("Minkowski bound in 6D:", (Mat.determinant().abs().n().log(2) / 6).n())

# Run LLL and BKZ:
from fpylll import IntegerMatrix, LLL, BKZ
fMat = IntegerMatrix(6, 6)
for i in range(6):
    for j in range(6):
        fMat[i, j] = int(Mat[i, j])

LLL.reduction(fMat)
print("Shortest vector after LLL:", [int(fMat[0, j]).bit_length() for j in range(6)])
print("Norm after LLL:", vector(ZZ, [int(fMat[0, j]) for j in range(6)]).norm().n().log(2))

# Run BKZ with block size 60 (exact HKZ):
BKZ.reduction(fMat, BKZ.Param(block_size=6))
print("Shortest vector after BKZ-6:", [int(fMat[0, j]).bit_length() for j in range(6)])
print("Norm after BKZ-6:", vector(ZZ, [int(fMat[0, j]) for j in range(6)]).norm().n().log(2))

for row_idx in range(6):
    r = [int(fMat[row_idx, j]) for j in range(6)]
    u_cand = r[0] // W
    v_cand = r[1] // W
    w_cand = r[2] // W
    A0_cand = r[3]
    A1_cand = r[4]
    A2_cand = r[5]
    print(f"Row {row_idx}: norm bits = {vector(ZZ, r).norm().n().log(2):.1f}")
    print(f"  u_cand={u_cand.bit_length()}b, v_cand={v_cand.bit_length()}b, w_cand={w_cand.bit_length()}b")
    print(f"  u*w == v^2?: {u_cand * w_cand == v_cand^2}")
