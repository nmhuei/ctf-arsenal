with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

# Target equation:
# k0 * h0 - k1 * h1 + k2 * h2 = 2 * n
# Vector: (k0, k1, k2) such that:
# k0 * h0 - k1 * h1 + k2 * h2 = 2 * n
# Let H_vec = (h0, -h1, h2)

H_vec = vector(ZZ, [h0, -h1, h2])

# Find particular solution:
# Solve H_vec . k = 2 * n over ZZ:
# Using xgcd:
g, s, t = xgcd(h0, -h1)
# g = s * h0 + t * (-h1)
g_all, u, w = xgcd(g, h2)
# g_all = u * g + w * h2 = u * s * h0 + u * t * (-h1) + w * h2
print("gcd of H_vec:", g_all)

# Particular solution:
mul = (2 * n) // g_all
k_part = vector(ZZ, [mul * u * s, mul * u * t, mul * w])
print("Check particular solution:", k_part * H_vec == 2 * n)

# Kernel of H_vec:
M_ker = Matrix(ZZ, [list(H_vec)]).right_kernel().basis_matrix().LLL()
print("Kernel basis norms:", [vector(r).norm().n().log(2) for r in M_ker.rows()])

# Babai nearest plane: find vector in M_ker closest to k_part:
# We want k = k_part - sum(c_i * M_ker[i]) to be small:
# CVP of k_part with respect to M_ker:
# Build embedding matrix:
M_cvp = Matrix(ZZ, 3, 3)
M_cvp[0] = M_ker[0]
M_cvp[1] = M_ker[1]
# Gram-Schmidt / solve over QQ:
k_approx = M_ker.solve_left(vector(QQ, k_part))
k_closest = vector(ZZ, [round(x) for x in k_approx]) * M_ker
k_short = k_part - k_closest

print("k_short * H_vec == 2 * n:", k_short * H_vec == 2 * n)
print("k_short bit lengths:", [abs(x).bit_length() for x in k_short])
print("k_short:", k_short)
