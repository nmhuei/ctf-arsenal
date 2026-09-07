import time
from Crypto.Util.number import getPrime, long_to_bytes

t0 = time.time()
print("[*] Testing square 50x50 triangular lattice...")
with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

M = Matrix(ZZ, [
    [h0, h1, h2],
    [n,  0,  0 ],
    [0,  n,  0 ],
    [0,  0,  n ]
])
HNF = M.hermite_form()
HNF_rows = [r for r in HNF.rows() if vector(r).norm() > 0]
L = Matrix(ZZ, HNF_rows).LLL()

H = vector(ZZ, [h0, h1, h2])
c = vector(ZZ, [ZZ(x) for x in L.solve_left(H)])

ks = [(L[i][0] * pow(int(h0), -1, n)) % n for i in range(3)]

R.<w0, w1, w2> = ZZ[]

# Even monomials up to degree 6:
monos = []
deg_monos = {0: [], 2: [], 4: [], 6: []}
for deg in [0, 2, 4, 6]:
    for i in range(deg, -1, -1):
        for j in range(deg - i, -1, -1):
            k = deg - i - j
            m = w0^i * w1^j * w2^k
            monos.append(m)
            deg_monos[deg].append(m)

n_monos = len(monos)
print(f"Total monomials: {n_monos}")

W0 = 1 << (abs(c[0]).bit_length() + 1)
W1 = 1 << (abs(c[1]).bit_length() + 1)
W2 = 1 << (abs(c[2]).bit_length() + 1)

col_weights = []
for m in monos:
    exp = m.exponents()[0]
    col_weights.append(W0^exp[0] * W1^exp[1] * W2^exp[2])

# Build triangular basis:
# For each monomial m, we assign a polynomial P whose leading monomial is m.
# Target power of n:
# deg 0: n^3
# deg 2: n^2
# deg 4: n^1
# deg 6: n^0

# 4 Base polynomials:
raw_polys = [(ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1]
for j in range(3):
    raw_polys.append((w0*L[0, j] + w1*L[1, j] + w2*L[2, j])^2 - H[j]^2)

E = []
for P in raw_polys:
    E.append(sum(((P.monomial_coefficient(m) % n)) * m for m in deg_monos[2] + [R(1)]))

# Pool of available polynomials:
pool = []
# Group 1: E_i * E_j * E_k (deg 6, n^0)
for i in range(4):
    for j in range(i, 4):
        for k in range(j, 4):
            pool.append(E[i] * E[j] * E[k])

# Group 2: n * m2 * E_i * E_j (deg 6, n^1)
for m in deg_monos[2]:
    for i in range(4):
        for j in range(i, 4):
            pool.append(n * m * E[i] * E[j])

# Group 3: n * E_i * E_j (deg 4, n^1)
for i in range(4):
    for j in range(i, 4):
        pool.append(n * E[i] * E[j])

# Group 4: n^2 * m4 * E_k (deg 6, n^2)
for m in deg_monos[4]:
    for k in range(4):
        pool.append((n^2) * m * E[k])

# Group 5: n^2 * m2 * E_k (deg 4, n^2)
for m in deg_monos[2]:
    for k in range(4):
        pool.append((n^2) * m * E[k])

# Group 6: n^2 * E_k (deg 2, n^2)
for k in range(4):
    pool.append((n^2) * E[k])

# Sort monos by degree ascending, then lex:
# For each monomial, find the best polynomial in pool with that leading monomial (or use n^(3 - deg//2) * m)
selected_polys = []
used_monos = set()

# Map polynomials by leading monomial:
for m in reversed(monos):
    best_P = None
    deg_m = m.total_degree()
    # default fallback:
    default_P = (n^(3 - deg_m // 2)) * m
    
    # Check if any P in pool has leading monomial m:
    for P in pool:
        # Check leading monomial in our order:
        coeffs = [(idx, P.monomial_coefficient(monos[idx])) for idx in range(n_monos)]
        nz_coeffs = [c for c in coeffs if c[1] != 0]
        if nz_coeffs and monos[nz_coeffs[-1][0]] == m:
            best_P = P
            break
    if best_P is not None:
        selected_polys.append(best_P)
    else:
        selected_polys.append(default_P)

print(f"Selected {len(selected_polys)} polynomials for 50 monomials!")
M_sq = Matrix(ZZ, n_monos, n_monos)
for r_idx, P in enumerate(selected_polys):
    for c_idx, m in enumerate(monos):
        M_sq[r_idx, c_idx] = P.monomial_coefficient(m) * col_weights[c_idx]

print(f"Matrix shape: {M_sq.dimensions()}, rank: {M_sq.rank()}")
print("Running LLL on square 50x50 matrix...")
t_lll = time.time()
L_sq = M_sq.LLL()
print(f"LLL completed in {time.time() - t_lll:.2f}s!")

target_norm_bits = (n^3).bit_length()
print(f"Target norm bits (n^3): {target_norm_bits}")

found = []
for idx, r in enumerate(L_sq.rows()):
    if vector(r).norm() == 0: continue
    norm = vector(r).norm().n()
    if norm.log(2) < target_norm_bits:
        P = sum((r[c_idx] // col_weights[c_idx]) * monos[c_idx] for c_idx in range(n_monos))
        if not P.is_constant():
            found.append((norm.log(2), P))

print(f"Found {len(found)} non-constant polynomials with norm < n^3!")
if found:
    print("Shortest norm bits:", found[0][0])
    R_qq.<w0, w1, w2> = QQ[]
    for num_polys in [5, 10, 15, len(found)]:
        subset = [R_qq(P) for nb, P in found[:num_polys]]
        I = ideal(subset)
        dim = I.dimension()
        print(f"Using top {num_polys} polynomials: ideal dimension = {dim}")
        if dim == 0:
            gb = I.groebner_basis()
            print(f"[+] Groebner basis found with {len(gb)} generators!")
            V = I.variety()
            print(f"[+] Variety solutions: {len(V)}")
            for sol in V:
                w_sol = (ZZ(sol[w0]), ZZ(sol[w1]), ZZ(sol[w2]))
                J = (ks[0]*w_sol[0] + ks[1]*w_sol[1] + ks[2]*w_sol[2]) % n
                p_cand = gcd(J - 1, n)
                if 1 < p_cand < n:
                    q_cand = n // p_cand
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
                    exit(0)
            break
