# Compute theoretical determinant and bound for Herrmann-May simultaneous linear mod p
# 2 polynomials: f1 = x1 - a1*x0, f2 = x2 - a2*x0
# p = n^0.5, n = 2^2048, X = 2^624

for m in [1, 2, 3, 4, 5, 6]:
    # Collect shift polynomials of degree <= m:
    # g_{j, k, l} = x0^l * f1^j * f2^k * n^(max(0, m - j - k))
    # with j + k + l <= m (or <= m + t)
    # Let's test degree d = m:
    shifts = []
    monos = set()
    for total_deg in range(1, m + 1):
        for j in range(total_deg + 1):
            for k in range(total_deg + 1 - j):
                l = total_deg - j - k
                shifts.append((j, k, l, max(0, m - j - k)))
    
    dim = len(shifts)
    # Total n-power:
    sum_n_pow = sum(s[3] for s in shifts)
    # Total x-power on each variable: by symmetry, equal for x0, x1, x2:
    sum_deg = sum(s[0] + s[1] + s[2] for s in shifts)
    sum_x_pow = sum_deg / 3.0
    
    # Target condition: X^(sum_x_pow) * n^(sum_n_pow) < p^(m * dim) = n^(0.5 * m * dim)
    # X^s_x < n^(0.5 * m * dim - s_n)
    # max_X = n^( (0.5 * m * dim - s_n) / s_x )
    gamma = (0.5 * m * dim - sum_n_pow) / sum_x_pow
    max_bits = gamma * 2048
    print(f"m = {m}: dim = {dim}, max_X = n^{gamma:.4f} = {max_bits:.1f} bits (our X = 624 bits)")
