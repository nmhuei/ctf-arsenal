with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

M = Matrix(ZZ, [
    [h0, h1, h2],
    [n,  0,  0 ],
    [0,  n,  0 ],
    [0,  0,  n ]
])
HNF = M.hermite_form()
HNF_rows = [r for r in HNF.rows() if vector(r).norm() > 0]
L = Matrix(ZZ, HNF_rows).LLL()

H = vector(ZZ, [h0, h1, h2])
c = vector(ZZ, [ZZ(x) for x in L.solve_left(H)])

M_ker = Matrix(ZZ, [hints]).right_kernel().basis_matrix().LLL()
v1 = M_ker[0]
v2 = M_ker[1]

z1 = vector(ZZ, [ZZ(x) for x in (2 * L * v1 / n)])
z2 = vector(ZZ, [ZZ(x) for x in (2 * L * v2 / n)])

Y1 = vector(ZZ, [
    c[1]*z1[2] - c[2]*z1[1],
    c[2]*z1[0] - c[0]*z1[2],
    c[0]*z1[1] - c[1]*z1[0]
])

Y2 = vector(ZZ, [
    c[1]*z2[2] - c[2]*z2[1],
    c[2]*z2[0] - c[0]*z2[2],
    c[0]*z2[1] - c[1]*z2[0]
])

Y3 = c
Y = Matrix(ZZ, [list(Y1), list(Y2), list(Y3)]).transpose()
adjY = Y.adjugate()
Delta_z = c * vector(ZZ, [z1[1]*z2[2]-z1[2]*z2[1], z1[2]*z2[0]-z1[0]*z2[2], z1[0]*z2[1]-z1[1]*z2[0]])

row0 = 2 * adjY[0]
row1 = 2 * adjY[1]

# Lattice of w such that:
# row0 . w = 0 mod Delta_z
# row1 . w = 0 mod Delta_z
# We want w with |w0| <= W0, |w1| <= W1, |w2| <= W2.

W0 = 1 << 285
W1 = 1 << 286
W2 = 1 << 283

# Build integer relations lattice in 3 variables:
# Congruence:
# (row0 . w) - k1 * Delta_z = 0
# (row1 . w) - k2 * Delta_z = 0

# Scale columns to balance norms:
W_max = max(W0, W1, W2)
col_scales = [W_max // W0, W_max // W1, W_max // W2]

# Matrix of the modular kernel:
M_cong = Matrix(ZZ, [
    [row0[0] % Delta_z, row0[1] % Delta_z, row0[2] % Delta_z],
    [row1[0] % Delta_z, row1[1] % Delta_z, row1[2] % Delta_z],
    [Delta_z, 0, 0],
    [0, Delta_z, 0],
    [0, 0, Delta_z]
])

# The kernel lattice of relations in w:
# In Sage, kernel modulo Delta_z:
# Let's find the lattice of w in Z^3 such that row0*w = 0 mod Delta_z and row1*w = 0 mod Delta_z:
A_sys = Matrix(ZZ, [
    [row0[0], row0[1], row0[2]],
    [row1[0], row1[1], row1[2]]
])

# Kernel of A_sys over ZZ / Delta_z:
# That is: w in Z^3 such that A_sys * w = Delta_z * k
# Dual lattice / orthogonal lattice:
# We can use a 5-dim lattice:
# [ Delta_z*I_2 | A_sys ]
# [    0        |   I_3 ]
M_lat = Matrix(ZZ, 5, 5)
M_lat[0, 0] = Delta_z
M_lat[1, 1] = Delta_z
for i in range(2):
    for j in range(3):
        M_lat[i, 2 + j] = A_sys[i, j]

# We want row linear combination to cancel the first 2 columns:
# Standard kernel lattice construction:
# Ker = A_sys.right_kernel_matrix() or similar
K = Matrix(ZZ, [
    list(row0),
    list(row1)
])

# Find integer kernel of K mod Delta_z:
print("Computing kernel mod Delta_z...")
M_full = Matrix(ZZ, [
    [Delta_z, 0, 0, 0, 0],
    [0, Delta_z, 0, 0, 0],
    [row0[0], row1[0], col_scales[0], 0, 0],
    [row0[1], row1[1], 0, col_scales[1], 0],
    [row0[2], row1[2], 0, 0, col_scales[2]]
])

# Large scaling on the congruence columns:
K_factor = 1 << 600
M_scaled = Matrix(ZZ, 5, 5)
for i in range(5):
    for j in range(5):
        M_scaled[i, j] = M_full[i, j]
M_scaled[0, 0] *= K_factor
M_scaled[1, 1] *= K_factor
M_scaled[2, 0] *= K_factor
M_scaled[2, 1] *= K_factor
M_scaled[3, 0] *= K_factor
M_scaled[3, 1] *= K_factor
M_scaled[4, 0] *= K_factor
M_scaled[4, 1] *= K_factor

L_red = M_scaled.LLL()
print("LLL completed! Shortest rows:")
for r in L_red.rows():
    if vector(r).norm() > 0:
        w_cand = [r[2] // col_scales[0], r[3] // col_scales[1], r[4] // col_scales[2]]
        norm_w = vector(ZZ, w_cand).norm().n()
        print(f"w_cand = {w_cand}, norm bits = {norm_w.log(2):.1f}")
        
        # Test if w_cand factors n:
        ks = [(L[i][0] * pow(int(h0), -1, n)) % n for i in range(3)]
        J = (ks[0]*w_cand[0] + ks[1]*w_cand[1] + ks[2]*w_cand[2]) % n
        p_cand = gcd(J - 1, n)
        if 1 < p_cand < n:
            print(f"[!] SUCCESS! Factored n! p = {p_cand}")
            break
