# Herrmann-May / Jochemsz-May lattice for 2 linear polynomials mod p:
# f1 = x1 - a1*x0, f2 = x2 - a2*x0
# Shifts: g_{j, k, l} = f1^j * f2^k * x0^l * n^(max(0, m - j - k))
# with j + k <= m and j + k + l <= d_max.
# Let's optimize d_max = m + t for each m:

p_power = 0.5 # p = n^0.5
n_bits = 2048

for m in range(2, 12):
    best_gamma = 0
    best_t = 0
    best_dim = 0
    for t in range(0, 8):
        d_max = m + t
        shifts = []
        for d in range(1, d_max + 1):
            for j in range(d + 1):
                for k in range(d + 1 - j):
                    if j + k <= m:
                        l = d - j - k
                        n_exp = m - j - k
                        shifts.append((j, k, l, n_exp))
        dim = len(shifts)
        sum_n = sum(s[3] for s in shifts)
        # Monomials in this set:
        # All monomials of degree 1..d_max:
        # But we only use homogeneous of each degree!
        # Determinant calculation:
        # Diagonal elements: each shift has leading monomial with coeff n^n_exp
        # The weight of monomial of degree d is X^d
        sum_X = sum(s[0] + s[1] + s[2] for s in shifts)
        # Condition: det < p^(m * dim) = n^(0.5 * m * dim)
        # n^(sum_n) * X^(sum_X) < n^(0.5 * m * dim)
        # X < n^( (0.5 * m * dim - sum_n) / sum_X )
        gamma = (0.5 * m * dim - sum_n) / sum_X
        if gamma > best_gamma:
            best_gamma = gamma
            best_t = t
            best_dim = dim
    max_bits = best_gamma * n_bits
    print(f"m = {m:2d}, best t = {best_t}: dim = {best_dim:3d}, max_X = n^{best_gamma:.4f} = {max_bits:.1f} bits")
