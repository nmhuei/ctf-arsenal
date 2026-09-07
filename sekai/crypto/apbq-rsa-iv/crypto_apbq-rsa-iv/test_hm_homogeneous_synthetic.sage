load('test_Q_K_mod_MK.sage')

# In synthetic:
# a = (a0, a1, a2)
# h = p*a + q*b
# a0, a1, a2 <= X_bound
X_bound = max(a) * 2
print("Synthetic X_bound bits:", X_bound.nbits())
print("Synthetic n bits:", n.nbits())
print("Synthetic q bits:", q.nbits())

# Two equations modulo q:
# f1 = h1*x0 - h0*x1 = - q*Delta01 = 0 mod q
# f2 = h2*x0 - h0*x2 = - q*Delta02 = 0 mod q

R.<x0, x1, x2> = ZZ[]
f1 = h[1]*x0 - h[0]*x1
f2 = h[2]*x0 - h[0]*x2

# Check roots:
assert f1(a[0], a[1], a[2]) % q == 0
assert f2(a[0], a[1], a[2]) % q == 0

# Try different (m, t):
for m in [2, 3, 4]:
    for t in range(1, m + 1):
        # Monomials of pure degree m:
        monos = []
        for d0 in range(m, -1, -1):
            for d1 in range(m - d0, -1, -1):
                d2 = m - d0 - d1
                monos.append(x0^d0 * x1^d1 * x2^d2)
        
        # Shift polynomials:
        shifts = []
        for j in range(m + 1):
            for k in range(m + 1 - j):
                # degree of f1^j * f2^k is j + k
                rem_deg = m - j - k
                # multiply by x0^(rem_deg - l) * x1^l
                for l in range(rem_deg + 1):
                    mult = n^max(0, t - j - k)
                    poly = mult * (f1^j) * (f2^k) * (x0^(rem_deg - l)) * (x1^l)
                    shifts.append(poly)
        
        # Build lattice matrix:
        weights = [X_bound^m for _ in monos]
        M = Matrix(ZZ, len(shifts), len(monos))
        for r_idx, poly in enumerate(shifts):
            for c_idx, mono in enumerate(monos):
                M[r_idx, c_idx] = poly.monomial_coefficient(mono) * weights[c_idx]
        
        # Reduce rows:
        M_red = M.LLL()
        
        # Check target bound: Howgrave-Graham bound is q^t
        target_norm = (q^t).n()
        
        # Count short vectors:
        short_polys = []
        short_vecs = []
        for r in M_red.rows():
            r_vec = vector(ZZ, r)
            if r_vec.norm() > 0:
                # unweighted poly:
                p_unw = sum((r[c_idx] // weights[c_idx]) * monos[c_idx] for c_idx in range(len(monos)))
                if p_unw(a[0], a[1], a[2]) == 0:
                    short_polys.append(p_unw)
                    short_vecs.append(vector(ZZ, [r[c_idx] // weights[c_idx] for c_idx in range(len(monos))]))
        
        print(f"m={m}, t={t}: dim={len(monos)}, shifts={len(shifts)}, vanishing polys={len(short_polys)}")
        if len(short_vecs) >= len(monos) - 1:
            print("  ==> Found enough short vectors! Checking kernel...")
            M_short = Matrix(ZZ, short_vecs)
            ker = M_short.right_kernel().basis_matrix()
            print("  Kernel rank:", ker.rank())
            if ker.rank() == 1:
                r_cand = ker[0]
                # Check if r_cand is proportional to true root vector:
                r_true = vector(ZZ, [mono(a[0], a[1], a[2]) for mono in monos])
                print("  r_cand proportional to r_true?:", r_cand.cross_product(r_true) == 0 if len(monos)==3 else "dim>3")
                # Check ratios:
                # find mono x0^m, x0^(m-1)*x1, x0^(m-1)*x2:
                idx0 = monos.index(x0^m)
                idx1 = monos.index(x0^(m-1) * x1)
                idx2 = monos.index(x0^(m-1) * x2)
                ratio1 = QQ(r_cand[idx1]) / QQ(r_cand[idx0])
                ratio2 = QQ(r_cand[idx2]) / QQ(r_cand[idx0])
                print(f"  ratio1 == a1/a0: {ratio1 == QQ(a[1])/QQ(a[0])}")
                print(f"  ratio2 == a2/a0: {ratio2 == QQ(a[2])/QQ(a[0])}")
                break
    else:
        continue
    break
