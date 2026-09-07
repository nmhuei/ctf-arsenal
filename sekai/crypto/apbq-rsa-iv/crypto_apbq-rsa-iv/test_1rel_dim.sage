n_bits = 2048.0
X_bits = 190.0

# 1 relation in 3 variables: f(x, y, z) = x + a1*y + a2*z = 0 mod p
# Monomials: x^j * y^k * z^l with j + k + l <= m + t
# Shifts: g_{j, k, l} = f^j * y^k * z^l * n^(max(0, m - j))
# In this case, f has leading term x, so monomials are the same as shifts.
# Condition: det(M) < p^(m * dim) = n^(0.5 * m * dim)
# det(M) = n^(sum_n) * X^(sum_deg) where sum_deg is total degree on x, y, z
# X^(sum_deg) < n^(0.5 * m * dim - sum_n)
# X < n^( (0.5 * m * dim - sum_n) / sum_deg )

for m in range(1, 15):
    for t in range(0, 15):
        # We need shifts that optimize the bound:
        # In Herrmann-May (2008) Section 3:
        # For 1 relation in k variables:
        # Shifts are: f^j * x_2^i2 * ... * x_k^ik * n^(m - j)
        polys = []
        for j in range(m + t + 1):
            n_pow = max(0, m - j)
            for k in range(m + t + 1 - j):
                for l in range(m + t + 1 - j - k):
                    deg = j + k + l
                    polys.append((j, k, l, n_pow, deg))
        dim = len(polys)
        sum_n = sum(p[3] for p in polys)
        sum_deg = sum(p[4] for p in polys)
        diff = 0.5 * m * dim - sum_n
        if diff > 0 and sum_deg > 0:
            gamma = diff / sum_deg
            bits = gamma * n_bits
            if bits > 150:
                print(f"m = {m}, t = {t}: dim = {dim}, max_X = {float(bits):.1f} bits")
