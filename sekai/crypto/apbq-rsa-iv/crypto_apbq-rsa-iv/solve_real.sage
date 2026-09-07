from Crypto.Util.number import bytes_to_long, long_to_bytes
import time

with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

print("Running lattice solver on real challenge...")
t0 = time.time()

factored = False
found_factors = []

# Try all 3 choices of base hint h_pivot
for pivot in range(3):
    other = [i for i in range(3) if i != pivot]
    i1, i2 = other[0], other[1]

    A1 = (hints[i1] * pow(hints[pivot], -1, n)) % n
    A2 = (hints[i2] * pow(hints[pivot], -1, n)) % n

    for monic_var in [0, 1, 2]:
        if monic_var == 0:
            c_pivot, c1, c2 = 1, A1, A2
        elif monic_var == 1:
            if gcd(A1, n) != 1: 
                g = gcd(A1, n)
                found_factors.append(g)
                factored = True
                break
            inv_A1 = pow(A1, -1, n)
            c_pivot, c1, c2 = inv_A1, 1, (A2 * inv_A1) % n
        else:
            if gcd(A2, n) != 1:
                g = gcd(A2, n)
                found_factors.append(g)
                factored = True
                break
            inv_A2 = pow(A2, -1, n)
            c_pivot, c1, c2 = inv_A2, (A1 * inv_A2) % n, 1

        R.<x0, x1, x2> = ZZ[]
        f = c_pivot * x0 + c1 * x1 + c2 * x2

        m = 4
        d = 4
        # Bound X is around 2^315
        X = 2**315

        monomials = []
        for m2 in range(d, -1, -1):
            for m1 in range(d - m2, -1, -1):
                m0 = d - m2 - m1
                monomials.append((m0, m1, m2))

        dim = len(monomials)
        mono_objs = [x0^m0 * x1^m1 * x2^m2 for m0, m1, m2 in monomials]

        polys = []
        for m0, m1, m2 in monomials:
            p_monic = m0 if monic_var == 0 else (m1 if monic_var == 1 else m2)
            if p_monic < m:
                poly = (f^p_monic) * (n^(m - p_monic))
                if monic_var == 0: poly = poly * (x1^m1) * (x2^m2)
                elif monic_var == 1: poly = poly * (x0^m0) * (x2^m2)
                else: poly = poly * (x0^m0) * (x1^m1)
            else:
                poly = (f^m)
                if monic_var == 0: poly = poly * (x0^(m0 - m)) * (x1^m1) * (x2^m2)
                elif monic_var == 1: poly = poly * (x1^(m1 - m)) * (x0^m0) * (x2^m2)
                else: poly = poly * (x2^(m2 - m)) * (x0^m0) * (x1^m1)
            polys.append(poly)

        M = Matrix(ZZ, dim, dim)
        for r in range(dim):
            for c in range(dim):
                M[r, c] = polys[r].monomial_coefficient(mono_objs[c]) * (X^d)

        print(f"Pivot {pivot}, monic {monic_var}: running LLL...")
        L = M.LLL()

        for row_idx in range(dim):
            poly = sum((L[row_idx, c] // (X^d)) * mono_objs[c] for c in range(dim))
            factors = poly.factor()
            for fac, _ in factors:
                if hasattr(fac, 'total_degree') and fac.total_degree() == 1:
                    k0 = fac.monomial_coefficient(x0)
                    k1 = fac.monomial_coefficient(x1)
                    k2 = fac.monomial_coefficient(x2)
                    k_orig = [0, 0, 0]
                    k_orig[pivot] = k0
                    k_orig[i1] = k1
                    k_orig[i2] = k2
                    for val in [k_orig[0]*hints[1] - k_orig[1]*hints[0], 
                                k_orig[0]*hints[2] - k_orig[2]*hints[0], 
                                k_orig[1]*hints[2] - k_orig[2]*hints[1]]:
                        g = gcd(val, n)
                        if 1 < g < n:
                            print(f"SUCCESS! Found factor: {g}")
                            found_factors.append(g)
                            factored = True
                            break
                if factored: break
            if factored: break
        if factored: break
    if factored: break

if factored:
    p_found = found_factors[0]
    q_found = n // p_found
    print(f"Factored n in {time.time() - t0:.2f}s!")
    print(f"p = {p_found}")
    print(f"q = {q_found}")
    
    phi = (p_found - 1) * (q_found - 1)
    d_priv = pow(65537, -1, phi)
    m_dec = pow(c, d_priv, n)
    flag = long_to_bytes(int(m_dec))
    print(f"FLAG: {flag}")
else:
    print(f"Failed with m=4, d=4 after {time.time() - t0:.2f}s")
