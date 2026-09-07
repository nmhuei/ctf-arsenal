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

    A1 = (h[1] * pow(h[0], -1, n)) % n
    A2 = (h[2] * pow(h[0], -1, n)) % n

    inv_A2 = pow(A2, -1, n)
    c1 = (A1 * inv_A2) % n
    c0 = (1 * inv_A2) % n

    R.<x0, x1, x2> = ZZ[]
    f = x2 + c1 * x1 + c0 * x0

    m = 2
    d = 2
    X = 2**10

    monomials = []
    for i2 in range(d, -1, -1):
        for i1 in range(d - i2, -1, -1):
            i0 = d - i2 - i1
            monomials.append((i0, i1, i2))

    polys = []
    for i0, i1, i2 in monomials:
        if i2 < m:
            poly = (x0^i0) * (x1^i1) * (f^i2) * (n^(m - i2))
        else:
            poly = (x0^i0) * (x1^i1) * (x2^(i2 - m)) * (f^m)
        polys.append(poly)

    dim = len(monomials)
    mono_objs = [x0^i0 * x1^i1 * x2^i2 for i0, i1, i2 in monomials]
    M = Matrix(ZZ, dim, dim)
    for r in range(dim):
        for c in range(dim):
            M[r, c] = polys[r].monomial_coefficient(mono_objs[c]) * (X^d)

    L = M.LLL()

    factored = False
    for row_idx in range(dim):
        poly = sum((L[row_idx, c] // (X^d)) * mono_objs[c] for c in range(dim))
        factors = poly.factor()
        for fac, _ in factors:
            if hasattr(fac, 'total_degree') and fac.total_degree() == 1:
                k0 = fac.monomial_coefficient(x0)
                k1 = fac.monomial_coefficient(x1)
                k2 = fac.monomial_coefficient(x2)
                # Test gcd
                for val in [k0*h[1] - k1*h[0], k0*h[2] - k2*h[0], k1*h[2] - k2*h[1]]:
                    g = gcd(val, n)
                    if 1 < g < n:
                        factored = True
                        break
            if factored: break
        if factored: break
    
    if factored:
        success += 1
        print(f"Trial {trial}: SUCCESS! Factored n!")
    else:
        print(f"Trial {trial}: FAILED")

print(f"Total successes: {success}/10")
