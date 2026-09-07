# Compute gamma for 2 linear equations mod p = n^0.5:
# f1 = x1 - a1*x0, f2 = x2 - a2*x0
# As m, t grow:
import sys

def compute_gamma(m, t):
    sum_n = 0
    total_deg = 0
    dim = 0
    for j in range(m + t + 1):
        for k in range(m + t + 1 - j):
            n_pow = max(0, m - j - k)
            for l in range(m + t + 1 - j - k):
                dim += 1
                sum_n += n_pow
                total_deg += (j + k + l)
    diff = 0.5 * m * dim - sum_n
    if diff > 0 and total_deg > 0:
        return diff / total_deg, dim
    return 0, dim

for m in [1, 2, 3, 5, 7, 10, 15, 20, 30]:
    best_gamma = 0
    best_t = 0
    best_dim = 0
    for t in range(int(m * 0.5), int(m * 2.0) + 1):
        g, d = compute_gamma(m, t)
        if g > best_gamma:
            best_gamma = g
            best_t = t
            best_dim = d
    print(f"m={m:2d}, t={best_t:2d}: dim={best_dim:6d}, gamma={best_gamma:.4f}, max_X={best_gamma * 2048:.1f} bits")
