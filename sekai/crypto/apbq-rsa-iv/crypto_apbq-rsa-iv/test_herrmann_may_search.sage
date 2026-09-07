# Search parameters m, t for 3-variable linear mod p: f = x + a1*y + a2*z
# Root bounds: X = Y = Z = 2^190. n = 2^2048, p = n^0.5

X_bits = 190.0
n_bits = 2048.0

print(f"Target X: {X_bits} bits ({X_bits / n_bits:.4f} * log2(n))")

for m in range(1, 10):
    for t in range(0, 10):
        # Monomials: x^i1 * y^i2 * z^i3 with i1 + i2 + i3 <= m + t
        # But f = x + a1*y + a2*z has leading term x.
        # Polynomials:
        # For j from 0 to m:
        #   g_{j, k, l} = f^j * y^k * z^l * n^(m - j) with j + k + l <= m + t
        # For j from m + 1 to m + t:
        #   h_{j, k, l} = f^j * y^k * z^l with j + k + l <= m + t
        
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
        
        # In symmetric variables x, y, z, average degree per variable: sum_deg / 3
        # Condition: n^sum_n * X^sum_deg < p^(m * dim) = n^(0.5 * m * dim)
        # X^sum_deg < n^(0.5 * m * dim - sum_n)
        # max_X = n^( (0.5 * m * dim - sum_n) / sum_deg )
        
        diff = 0.5 * m * dim - sum_n
        if diff > 0:
            gamma = diff / sum_deg
            max_X_bits = gamma * n_bits
            if max_X_bits > X_bits:
                print(f"[FOUND!] m = {m}, t = {t}: dim = {dim}, max_X = {max_X_bits:.1f} bits > {X_bits} bits!")
                break
