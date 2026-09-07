load('test_Q_K_mod_MK.sage')

X_bound = max(a) * 2
print("Synthetic X_bound bits:", X_bound.nbits())
print("Synthetic n bits:", n.nbits())
print("Synthetic q bits:", q.nbits())

C1 = (h[1] * pow(int(h[0]), -1, n)) % n
C2 = (h[2] * pow(int(h[0]), -1, n)) % n

R.<x0, x1, x2> = ZZ[]
f1 = x1 - C1 * x0
f2 = x2 - C2 * x0

# Check roots:
assert f1(a[0], a[1], a[2]) % q == 0
assert f2(a[0], a[1], a[2]) % q == 0

for m in [2, 3, 4, 5]:
    for t in range(1, m + 1):
        monos = []
        for d0 in range(m, -1, -1):
            for d1 in range(m - d0, -1, -1):
                d2 = m - d0 - d1
                monos.append(x0^d0 * x1^d1 * x2^d2)
        
        shifts = []
        for j in range(m + 1):
            for k in range(m + 1 - j):
                rem_deg = m - j - k
                for l in range(rem_deg + 1):
                    mult = n^max(0, t - j - k)
                    # Modulo n^t:
                    poly = mult * (f1^j) * (f2^k) * (x0^(rem_deg - l)) * (x1^l)
                    # We can reduce coefficients modulo n^t:
                    shifts.append(poly)
        
        weights = [X_bound^m for _ in monos]
        M = Matrix(ZZ, len(shifts), len(monos))
        for r_idx, poly in enumerate(shifts):
            for c_idx, mono in enumerate(monos):
                M[r_idx, c_idx] = (poly.monomial_coefficient(mono) % (n^t)) * weights[c_idx]
        
        # Add multiples of n^t for each monomial:
        M_full = Matrix(ZZ, len(shifts) + len(monos), len(monos))
        for r_idx in range(len(shifts)):
            for c_idx in range(len(monos)):
                M_full[r_idx, c_idx] = M[r_idx, c_idx]
        for c_idx in range(len(monos)):
            M_full[len(shifts) + c_idx, c_idx] = (n^t) * weights[c_idx]

        M_red = M_full.LLL()
        
        short_polys = []
        short_vecs = []
        for r in M_red.rows():
            r_vec = vector(ZZ, r)
            if r_vec.norm() > 0:
                p_unw = sum((r[c_idx] // weights[c_idx]) * monos[c_idx] for c_idx in range(len(monos)))
                if p_unw(a[0], a[1], a[2]) == 0:
                    short_polys.append(p_unw)
                    short_vecs.append(vector(ZZ, [r[c_idx] // weights[c_idx] for c_idx in range(len(monos))]))
        
        print(f"m={m}, t={t}: dim={len(monos)}, shifts={len(shifts)}, vanishing polys={len(short_polys)}")
        if len(short_vecs) >= len(monos) - 1:
            print(f"  ==> SUCCESS! Found {len(short_vecs)} short vectors in dimension {len(monos)}!")
            M_short = Matrix(ZZ, short_vecs)
            ker = M_short.right_kernel().basis_matrix()
            print("  Kernel rank:", ker.rank())
            if ker.rank() == 1:
                r_cand = ker[0]
                idx0 = monos.index(x0^m)
                idx1 = monos.index(x0^(m-1) * x1)
                idx2 = monos.index(x0^(m-1) * x2)
                ratio1 = QQ(r_cand[idx1]) / QQ(r_cand[idx0])
                ratio2 = QQ(r_cand[idx2]) / QQ(r_cand[idx0])
                print(f"  ratio1 == a1/a0: {ratio1 == QQ(a[1])/QQ(a[0])}")
                print(f"  ratio2 == a2/a0: {ratio2 == QQ(a[2])/QQ(a[0])}")
                exit(0)
