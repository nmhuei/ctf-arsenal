set_random_seed(42)

p_bits = 100
B_bits = 60

p = random_prime(2^p_bits, lbound=2^(p_bits-1))
q = random_prime(2^p_bits, lbound=2^(p_bits-1))
n = p * q

B = 1 << B_bits

a = [randint(1, B) for _ in range(3)]
b = [randint(1, B) for _ in range(3)]
h = [a[i] * p + b[i] * q for i in range(3)]

Delta01 = a[0]*b[1] - a[1]*b[0]
Delta02 = a[0]*b[2] - a[2]*b[0]
Delta12 = a[1]*b[2] - a[2]*b[1]
d_true = vector(ZZ, [Delta12, -Delta02, Delta01])

M_h = Matrix(ZZ, [h])
ker_h = M_h.right_kernel()
B_ker = ker_h.basis_matrix().LLL()
v1, v2 = B_ker.rows()
if vector(v1).cross_product(vector(v2)) != vector(h):
    if vector(v1).cross_product(vector(v2)) == -vector(h):
        v2 = -v2

mat_v = Matrix(ZZ, [v1, v2])
sol = mat_v.solve_left(d_true)
lam_true, mu_true = sol[0], sol[1]

print("True b:", b)
print("True lam:", lam_true, "True mu:", mu_true)
lam_p_true = p * lam_true
mu_p_true = p * mu_true

# Check the equations:
# eq 0: b0 = - h1^-1 * (lam_p * v1[2] + mu_p * v2[2]) mod h0
inv_h1_mod_h0 = pow(int(h[1]), -1, h[0])
w00 = (- inv_h1_mod_h0 * v1[2]) % h[0]
w01 = (- inv_h1_mod_h0 * v2[2]) % h[0]
print("Check eq 0:", (w00 * lam_p_true + w01 * mu_p_true) % h[0] == b[0])

# eq 1: b1 = h0^-1 * (lam_p * v1[2] + mu_p * v2[2]) mod h1
inv_h0_mod_h1 = pow(int(h[0]), -1, h[1])
w10 = (inv_h0_mod_h1 * v1[2]) % h[1]
w11 = (inv_h0_mod_h1 * v2[2]) % h[1]
print("Check eq 1:", (w10 * lam_p_true + w11 * mu_p_true) % h[1] == b[1])

# eq 2: b2 = - h0^-1 * (lam_p * v1[1] + mu_p * v2[1]) mod h2
inv_h0_mod_h2 = pow(int(h[0]), -1, h[2])
w20 = (- inv_h0_mod_h2 * v1[1]) % h[2]
w21 = (- inv_h0_mod_h2 * v2[1]) % h[2]
print("Check eq 2:", (w20 * lam_p_true + w21 * mu_p_true) % h[2] == b[2])

# Build 5D lattice:
# Variables: (x1, x2, b0, b1, b2) = (lam_p, mu_p, b0, b1, b2)
# Relations:
# w00 * x1 + w01 * x2 - b0 = k0 * h0
# w10 * x1 + w11 * x2 - b1 = k1 * h1
# w20 * x1 + w21 * x2 - b2 = k2 * h2

# Basis matrix:
# Row 0: [h0, 0, 0, 0, 0]
# Row 1: [0, h1, 0, 0, 0]
# Row 2: [0, 0, h2, 0, 0]
# Row 3: [w00, w10, w20, W_x, 0]
# Row 4: [w01, w11, w21, 0, W_x]

# Bounds:
# x1, x2 are ~ 2^(100 + 40) = 2^140
# b0, b1, b2 are ~ 2^60
# Scale b_i by W_b = 2^80, W_x = 1:
# Then target vector is:
# (k0*h0 + b0, ...) -> wait!
# The vector (k0, k1, k2, x1, x2) * M gives:
# [w00*x1 + w01*x2 + k0*h0, w10*x1 + w11*x2 + k1*h1, w20*x1 + w21*x2 + k2*h2, x1*W_x, x2*W_x]
# = [b0, b1, b2, x1*W_x, x2*W_x]!
# If we weight the columns by:
# [W_b, W_b, W_b, 1, 1]
# where W_b = 2^80!
# Then the target vector has entries:
# [b0 * W_b, b1 * W_b, b2 * W_b, x1, x2]
# All entries have size ~ 2^140!

W_b = 1 << (140 - 60) # 2^80

M = Matrix(ZZ, [
    [h[0] * W_b, 0, 0, 0, 0],
    [0, h[1] * W_b, 0, 0, 0],
    [0, 0, h[2] * W_b, 0, 0],
    [w00 * W_b, w10 * W_b, w20 * W_b, 1, 0],
    [w01 * W_b, w11 * W_b, w21 * W_b, 0, 1]
])

print("\n[*] Running LLL on 5x5 lattice...")
L_red = M.LLL()
print("[+] LLL done!")

for idx, r in enumerate(L_red.rows()):
    b0_cand = abs(r[0]) // W_b
    b1_cand = abs(r[1]) // W_b
    b2_cand = abs(r[2]) // W_b
    x1_cand = abs(r[3])
    x2_cand = abs(r[4])
    norm_bits = vector(r).norm().n().log(2)
    print(f"Row {idx}: norm bits = {norm_bits:.1f}")
    print(f"  b_cand = ({b0_cand}, {b1_cand}, {b2_cand})")
    print(f"  Matches true b?: {[b0_cand, b1_cand, b2_cand] == b}")
    # Check gcd:
    if b0_cand > 0 and b1_cand > 0:
        g = gcd(b1_cand * h[0] - b0_cand * h[1], n)
        if 1 < g < n:
            print(f"  [!] FACTORED N! g = {g} (p={p == g or q == g})")
