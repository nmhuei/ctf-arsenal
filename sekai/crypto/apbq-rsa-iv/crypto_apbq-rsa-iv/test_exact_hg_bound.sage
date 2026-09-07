# Exact Howgrave-Graham bound calculation for 2 relations mod p = n^0.5:
# f1 = x1 - a1*x0, f2 = x2 - a2*x0
# Root: (b0, b1, b2) with |b_i| <= X.
# We want to find the maximum X such that:
# det(L) < p^(m * dim) / sqrt(dim) = n^(0.5 * m * dim) / sqrt(dim)

n_bits = 2048.0

print("Exact bound search:")
for m in range(1, 8):
    for t in range(0, 8):
        # Shift polynomials:
        # For j + k <= m:
        #   g_{j, k, l} = f1^j * f2^k * x0^l * n^(m - j - k)
        # For j + k > m (from m+1 to m+t):
        #   h_{j, k, l} = f1^j * f2^k * x0^l
        # with j + k + l <= m + t.
        # Notice: f1 has leading term x1, f2 has leading term x2.
        # The leading monomials are x1^j * x2^k * x0^l.
        # The number of such monomials is the number of (j, k, l) with j + k + l <= m + t!
        # The matrix is triangular with diagonal entries:
        # diag = n^(max(0, m - j - k)) * X^(j + k + l)
        
        sum_n = 0
        sum_deg_x0 = 0
        sum_deg_x1 = 0
        sum_deg_x2 = 0
        dim = 0
        
        for j in range(m + t + 1):
            for k in range(m + t + 1 - j):
                n_pow = max(0, m - j - k)
                for l in range(m + t + 1 - j - k):
                    dim += 1
                    sum_n += n_pow
                    sum_deg_x1 += j
                    sum_deg_x2 += k
                    sum_deg_x0 += l
        
        total_deg = sum_deg_x0 + sum_deg_x1 + sum_deg_x2
        # Since X0 = X1 = X2 = X:
        # det(L) = n^(sum_n) * X^(total_deg)
        # Condition: det(L) < n^(0.5 * m * dim)
        # X^(total_deg) < n^(0.5 * m * dim - sum_n)
        diff = 0.5 * m * dim - sum_n
        if diff > 0 and total_deg > 0:
            gamma = diff / total_deg
            bits = gamma * n_bits
            if bits > 200:
                print(f"m = {m}, t = {t}: dim = {dim}, gamma = {float(gamma):.4f}, max_X = {float(bits):.1f} bits")
