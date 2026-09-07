import time
from Crypto.Util.number import long_to_bytes

t_start = time.time()
print("[*] Loading real challenge parameters...")
with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

# alpha1 = h1 * h0^-1 mod n
# alpha2 = h2 * h0^-1 mod n
inv_h0 = pow(int(h0), -1, n)
alpha1 = (h1 * inv_h0) % n
alpha2 = (h2 * inv_h0) % n

print(f"[+] alpha1 bit length: {alpha1.bit_length()}")
print(f"[+] alpha2 bit length: {alpha2.bit_length()}")

# Target root bound: X = 2^624
# Set X = 2^625 for safety margin:
X = 1 << 625

# Polynomial ring in x0, x1, x2:
R.<x0, x1, x2> = PolynomialRing(ZZ)
f1 = x1 - alpha1 * x0
f2 = x2 - alpha2 * x0

monos = [R(1), x0, x1, x2, x0^2, x0*x1, x0*x2, x1^2, x1*x2, x2^2]
polys = [
    R(n),
    n * x0,
    n * x0^2,
    f1,
    f1 * x0,
    f2,
    f2 * x0,
    f1^2,
    f1 * f2,
    f2^2
]

weights = [X^(m.total_degree()) for m in monos]
M = Matrix(ZZ, 10, 10)
for i, poly in enumerate(polys):
    for j, m in enumerate(monos):
        M[i, j] = poly.monomial_coefficient(m) * weights[j]

print("[*] Running LLL on 10x10 lattice...")
t_lll = time.time()
L_red = M.LLL()
print(f"[+] LLL completed in {time.time() - t_lll:.3f}s!")

# Theoretical bound for p is ~ 2^1024
target_bound = 1 << 1024
print(f"Target norm bound (p): {target_bound.bit_length()} bits")

polys_found = []
R_QQ.<y0, y1, y2> = PolynomialRing(QQ)

for idx, r in enumerate(L_red.rows()):
    norm_bits = vector(r).norm().n().log(2)
    print(f"Row {idx}: norm bits = {norm_bits:.1f}")
    if norm_bits < 1024:
        poly_cand = sum((r[j] // weights[j]) * monos[j] for j in range(10))
        polys_found.append(R_QQ(poly_cand))

print(f"[+] Number of short polynomials: {len(polys_found)}")

# Solve using algebraic variety / resultant:
# Substitute y2 = 1:
R2.<z0, z1> = PolynomialRing(QQ)
polys_sub = [p(z0, z1, 1) for p in polys_found]
J = ideal(polys_sub)
print(f"[*] Ideal dimension: {J.dimension()}")

variety = J.variety()
print(f"[*] Variety solutions count: {len(variety)}")
for sol in variety:
    print("Candidate sol:", sol)
    rat0 = sol[z0]
    rat1 = sol[z1]
    # rat0 = b0 / b2, rat1 = b1 / b2
    # In integers:
    # b0 / b2 = rat0.numerator() / rat0.denominator()
    den = lcm(rat0.denominator(), rat1.denominator())
    b0_cand = ZZ(rat0 * den)
    b1_cand = ZZ(rat1 * den)
    b2_cand = ZZ(den)
    
    print(f"  b0_cand bits = {b0_cand.bit_length()}, b1_cand bits = {b1_cand.bit_length()}, b2_cand bits = {b2_cand.bit_length()}")
    
    # Check gcd:
    diff = b1_cand * h0 - b0_cand * h1
    p_cand = gcd(diff, n)
    if 1 < p_cand < n:
        q_cand = n // p_cand
        print("\n" + "="*50)
        print(f"[!] SUCCESS! Factored n!")
        print(f"p = {p_cand}")
        print(f"q = {q_cand}")
        phi = (p_cand - 1) * (q_cand - 1)
        d = pow(e, -1, phi)
        pt = pow(ct, d, n)
        flag = long_to_bytes(pt)
        print(f"[FLAG] {flag.decode()}")
        with open('FLAG.txt', 'w') as out_f:
            out_f.write(flag.decode() + '\n')
        print("="*50)
        exit(0)
