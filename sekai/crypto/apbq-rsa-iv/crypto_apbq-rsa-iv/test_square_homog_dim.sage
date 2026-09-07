p_power = 0.5
n_bits = 2048

for m in range(1, 20):
    dim = (m + 1) * (m + 2) // 2
    # Shifts: (j, k) with j + k <= m
    # Each shift has n-power = m - j - k
    sum_n = sum(m - j - k for j in range(m + 1) for k in range(m + 1 - j))
    # Each monomial has degree m, so total X power is m * dim
    sum_X = m * dim
    
    # Target: n^(sum_n) * X^(m * dim) < p^(m * dim) = n^(0.5 * m * dim)
    # X^(m * dim) < n^(0.5 * m * dim - sum_n)
    # X < n^( 0.5 - sum_n / (m * dim) )
    gamma = 0.5 - sum_n / (m * dim)
    max_bits = gamma * n_bits
    print(f"m = {m:2d}: dim = {dim:3d}, sum_n / (m*dim) = {float(sum_n / (m*dim)):.4f}, max_X = n^{float(gamma):.4f} = {float(max_bits):.1f} bits")
