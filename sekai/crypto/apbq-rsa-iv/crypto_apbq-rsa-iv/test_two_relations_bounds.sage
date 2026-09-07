# 2 relations in 3 variables mod p:
# f1 = x1 - a1*x0, f2 = x2 - a2*x0
# Shifts: f1^j * f2^k * x0^l * n^(max(0, m - j - k))
# with j + k <= m and j + k + l <= m + t

for m in range(1, 8):
    for t in range(0, 8):
        polys = []
        for j in range(m + t + 1):
            for k in range(m + t + 1 - j):
                if j + k <= m:
                    n_pow = m - j - k
                else:
                    n_pow = 0
                for l in range(m + t + 1 - j - k):
                    deg = j + k + l
                    polys.append((j, k, l, n_pow, deg))
        dim = len(polys)
        sum_n = sum(p[3] for p in polys)
        sum_deg = sum(p[4] for p in polys)
        # Average degree on each of the 3 variables: sum_deg / 3
        # condition: n^sum_n * X^sum_deg < n^(0.5 * m * dim)
        diff = 0.5 * m * dim - sum_n
        gamma = diff / (sum_deg / 3.0) if sum_deg > 0 else 0
        bits = gamma * 2048
        if bits > 500:
            print(f"m = {m}, t = {t}: dim = {dim}, max_X = {float(bits):.1f} bits (our X = 624 bits!)")
