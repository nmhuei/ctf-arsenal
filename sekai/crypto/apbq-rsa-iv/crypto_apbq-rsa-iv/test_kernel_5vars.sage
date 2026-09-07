with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

M_ker = Matrix(ZZ, [list(hints)]).right_kernel().basis_matrix().LLL()
v1 = M_ker[0]
v2 = M_ker[1]

# Variables: (b0, b1, b2, P, Q)
# Eq 1: -h1 * b0 + h0 * b1 + 0 * b2 - v1[2] * P - v2[2] * Q = 0
# Eq 2: -h2 * b0 + 0 * b1 + h0 * b2 - v1[1] * P - v2[1] * Q = 0
# Eq 3: 0 * b0 - h2 * b1 + h1 * b2 - v1[0] * P - v2[0] * Q = 0

M_sys = Matrix(ZZ, [
    [-h1, h0, 0, -v1[2], -v2[2]],
    [-h2, 0, h0, -v1[1], -v2[1]],
    [0, -h2, h1, -v1[0], -v2[0]]
])

print("M_sys rank:", M_sys.rank())
ker = M_sys.right_kernel().basis_matrix()
print("ker dimensions:", ker.dimensions())

# Weights on variables:
# b0, b1, b2 <= 2^624
# P, Q <= 2^1449
# Let's scale columns to equalize bounds:
# Max weight: 2^1449.
# Scale for b0, b1, b2: 1 << (1449 - 624) = 1 << 825.

scale_b = 1 << 825
W_mat = diagonal_matrix([scale_b, scale_b, scale_b, 1, 1])

ker_weighted = ker * W_mat
ker_lll = ker_weighted.LLL()

print("Reduced basis norms:")
for idx, r in enumerate(ker_lll.rows()):
    print(f"Row {idx}: norm bits = {vector(r).norm().n().log(2):.1f}")
    # Unscale:
    unscaled = [r[0] // scale_b, r[1] // scale_b, r[2] // scale_b, r[3], r[4]]
    print(f"  unscaled bits: {[abs(x).bit_length() for x in unscaled]}")
    # Test gcd(b0*h1 - b1*h0, n):
    b0_cand, b1_cand, b2_cand, P_cand, Q_cand = unscaled
    if b0_cand != 0 and b1_cand != 0:
        val = b0_cand * h1 - b1_cand * h0
        g = gcd(val, n)
        print(f"  gcd(b0*h1 - b1*h0, n) = {g}")
        if 1 < g < n:
            print(f"[!] FACTORED N! p = {g}")
            exit(0)
