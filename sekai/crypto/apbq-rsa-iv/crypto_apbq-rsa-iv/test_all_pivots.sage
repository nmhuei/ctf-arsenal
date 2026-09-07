import random
from Crypto.Util.number import getPrime

success = 0
for trial in range(10):
    p = getPrime(60)
    q = getPrime(60)
    n = p * q
    B = 2**18

    a = [random.randint(1, B) for _ in range(3)]
    b = [random.randint(1, B) for _ in range(3)]
    h = [a[i]*p + b[i]*q for i in range(3)]

    factored = False
    # Try all 3 choices of base hint h_pivot
    for pivot in range(3):
        other = [i for i in range(3) if i != pivot]
        i1, i2 = other[0], other[1]

        A1 = (h[i1] * pow(h[pivot], -1, n)) % n
        A2 = (h[i2] * pow(h[pivot], -1, n)) % n

        # We have: x_pivot + x1*A1 + x2*A2 = 0 mod p
        # Let's try making x_pivot, x1, or x2 monic:
        for monic_var in [0, 1, 2]:
            if monic_var == 0:
                # monic in x_pivot: f = x0 + A1*x1 + A2*x2
                c_pivot, c1, c2 = 1, A1, A2
            elif monic_var == 1:
                # monic in x1: f = x1 + inv(A1)*x0 + inv(A1)*A2*x2
                if gcd(A1, n) != 1: continue
                inv_A1 = pow(A1, -1, n)
                c_pivot, c1, c2 = inv_A1, 1, (A2 * inv_A1) % n
            else:
                # monic in x2:
                if gcd(A2, n) != 1: continue
                inv_A2 = pow(A2, -1, n)
                c_pivot, c1, c2 = inv_A2, (A1 * inv_A2) % n, 1

            R.<x0, x1, x2> = ZZ[]
            f = c_pivot * x0 + c1 * x1 + c2 * x2

            m = 3
            d = 3
            X = 2**10

            monomials = []
            for m2 in range(d, -1, -1):
                for m1 in range(d - m2, -1, -1):
                    m0 = d - m2 - m1
                    monomials.append((m0, m1, m2))

            dim = len(monomials)
            mono_objs = [x0^m0 * x1^m1 * x2^m2 for m0, m1, m2 in monomials]

            polys = []
            for m0, m1, m2 in monomials:
                # power of monic var:
                p_monic = m0 if monic_var == 0 else (m1 if monic_var == 1 else m2)
                if p_monic < m:
                    # divide out the monic var and replace by f:
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

            L = M.LLL()

            for row_idx in range(dim):
                poly = sum((L[row_idx, c] // (X^d)) * mono_objs[c] for c in range(dim))
                factors = poly.factor()
                for fac, _ in factors:
                    if hasattr(fac, 'total_degree') and fac.total_degree() == 1:
                        k0 = fac.monomial_coefficient(x0)
                        k1 = fac.monomial_coefficient(x1)
                        k2 = fac.monomial_coefficient(x2)
                        # Map back to original indices:
                        # x0 corresponds to pivot, x1 to i1, x2 to i2
                        k_orig = [0, 0, 0]
                        k_orig[pivot] = k0
                        k_orig[i1] = k1
                        k_orig[i2] = k2
                        for val in [k_orig[0]*h[1] - k_orig[1]*h[0], k_orig[0]*h[2] - k_orig[2]*h[0], k_orig[1]*h[2] - k_orig[2]*h[1]]:
                            g = gcd(val, n)
                            if 1 < g < n:
                                factored = True
                                break
                    if factored: break
                if factored: break
            if factored: break
        if factored: break

    if factored:
        success += 1
        print(f"Trial {trial}: SUCCESS!")
    else:
        print(f"Trial {trial}: FAILED")

print(f"Total successes: {success}/10")
