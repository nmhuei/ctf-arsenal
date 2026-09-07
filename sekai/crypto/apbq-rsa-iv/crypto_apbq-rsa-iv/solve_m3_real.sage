import time
from Crypto.Util.number import long_to_bytes

t_start = time.time()
print("[*] Loading challenge parameters...")
with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

# 1. Build public lattice Lambda in Z^3:
print("[*] Step 1: Building public lattice Lambda in Z^3...")
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
print(f"[+] Lattice reduced! c = {c}")
print(f"c bit lengths: {[abs(x).bit_length() for x in c]}")

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
print(f"[*] Total monomials: {n_monos}")

# 4 Base polynomials:
raw_polys = [(ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1]
for j in range(3):
    raw_polys.append((w0*L[0, j] + w1*L[1, j] + w2*L[2, j])^2 - H[j]^2)

E = []
for P in raw_polys:
    E.append(sum(((P.monomial_coefficient(m) % n)) * m for m in deg_monos[2] + [R(1)]))

all_polys = []

# Group 1: E_i * E_j * E_k (mod n^3)
for i in range(4):
    for j in range(i, 4):
        for k in range(j, 4):
            all_polys.append(E[i] * E[j] * E[k])

# Group 2: n * m2 * E_i * E_j
for m in deg_monos[2]:
    for i in range(4):
        for j in range(i, 4):
            all_polys.append(n * m * E[i] * E[j])

# Group 3: n * E_i * E_j
for i in range(4):
    for j in range(i, 4):
        all_polys.append(n * E[i] * E[j])

# Group 4: n^2 * m4 * E_k
for m in deg_monos[4]:
    for k in range(4):
        all_polys.append((n^2) * m * E[k])

# Group 5: n^2 * m2 * E_k
for m in deg_monos[2]:
    for k in range(4):
        all_polys.append((n^2) * m * E[k])

# Group 6: n^2 * E_k
for k in range(4):
    all_polys.append((n^2) * E[k])

# Group 7: n^3 * m
for m in monos[:-1]:
    all_polys.append((n^3) * m)

print(f"[*] Total polynomials: {len(all_polys)}")

W0 = 1 << (abs(c[0]).bit_length() + 1)
W1 = 1 << (abs(c[1]).bit_length() + 1)
W2 = 1 << (abs(c[2]).bit_length() + 1)

col_weights = []
for m in monos:
    exp = m.exponents()[0]
    col_weights.append(W0^exp[0] * W1^exp[1] * W2^exp[2])

M_hg = Matrix(ZZ, len(all_polys), n_monos)
for r_idx, P in enumerate(all_polys):
    for c_idx, m in enumerate(monos):
        M_hg[r_idx, c_idx] = P.monomial_coefficient(m) * col_weights[c_idx]

print(f"[*] Step 2: Running LLL on {len(all_polys)}x{n_monos} lattice...")
t_lll = time.time()
L_hg = M_hg.LLL()
print(f"[+] LLL completed in {time.time() - t_lll:.2f}s!")

target_norm_bits = (n^3).bit_length()
print(f"Target norm bits (n^3): {target_norm_bits}")

found_polys = []
for idx, r in enumerate(L_hg.rows()):
    if vector(r).norm() == 0: continue
    norm = vector(r).norm().n()
    if norm.log(2) < target_norm_bits:
        P = sum((r[c_idx] // col_weights[c_idx]) * monos[c_idx] for c_idx in range(n_monos))
        if not P.is_constant():
            found_polys.append((norm.log(2), P))

print(f"[+] Found {len(found_polys)} non-constant polynomials with norm < n^3!")
for idx, (nb, P) in enumerate(found_polys[:10]):
    print(f"  Poly {idx}: norm bits = {nb:.1f}")

if found_polys:
    print("[*] Step 3: Computing Groebner basis over QQ...")
    R_qq.<w0, w1, w2> = QQ[]
    for num_polys in [5, 10, 15, 20, len(found_polys)]:
        subset = [R_qq(P) for nb, P in found_polys[:num_polys]]
        I = ideal(subset)
        dim = I.dimension()
        print(f"Using top {num_polys} polynomials: ideal dimension = {dim}")
        if dim == 0:
            gb = I.groebner_basis()
            print(f"[+] Groebner basis found with {len(gb)} generators!")
            for g in gb:
                print(" ", g)
            
            # Find variety:
            V = I.variety()
            print(f"[+] Variety solutions: {len(V)}")
            for sol in V:
                print("  Sol:", sol)
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
