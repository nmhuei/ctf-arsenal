import time
from Crypto.Util.number import long_to_bytes

t0 = time.time()
print("[*] Loading challenge parameters...")
with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

# 1. Build public lattice Lambda in Z^3:
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

R.<x, y> = ZZ[]
monos = []
for deg in range(4):
    for i in range(deg, -1, -1):
        monos.append(x^i * y^(deg - i))

n_monos = len(monos)
print(f"Total monomials up to degree 3: {n_monos}")

polys = []
for j in range(3):
    u = x * L[0, j] + y * L[1, j]
    F = u^2 - H[j] * u
    polys.append(F)
    polys.append(x * F)
    polys.append(y * F)

all_polys = list(polys)
for m in monos:
    all_polys.append(n * m)

print(f"Total polynomials: {len(all_polys)}")

X_bound = 1 << 286
Y_bound = 1 << 286

col_weights = []
for m in monos:
    exp = m.exponents()[0]
    col_weights.append(X_bound^exp[0] * Y_bound^exp[1])

M_hg = Matrix(ZZ, len(all_polys), n_monos)
for r_idx, P in enumerate(all_polys):
    for c_idx, m in enumerate(monos):
        M_hg[r_idx, c_idx] = P.monomial_coefficient(m) * col_weights[c_idx]

print("[*] Running LLL on Howgrave-Graham matrix...")
t_lll = time.time()
L_hg = M_hg.LLL()
print(f"[+] LLL completed in {time.time() - t_lll:.2f}s!")

found_polys = []
for idx, r in enumerate(L_hg.rows()):
    if vector(r).norm() == 0: continue
    norm = vector(r).norm().n()
    print(f"Row {idx}: norm bits = {norm.log(2):.1f}, n bits = {n.bit_length()}")
    if norm.log(2) < n.bit_length():
        P = sum((r[c_idx] // col_weights[c_idx]) * monos[c_idx] for c_idx in range(n_monos))
        if not P.is_constant():
            found_polys.append(P)

print(f"Found {len(found_polys)} polynomials with norm < n!")

if len(found_polys) >= 2:
    print("[*] Computing resultant of first two polynomials...")
    res = found_polys[0].resultant(found_polys[1], y)
    roots = res.univariate_polynomial().roots(multiplicities=False)
    print("Roots for x:", roots)
    for rx in roots:
        P_y = found_polys[0](rx, y).univariate_polynomial()
        for ry in P_y.roots(multiplicities=False):
            print(f"Candidate root: ({rx}, {ry})")
            for j in range(3):
                u_cand = rx * L[0, j] + ry * L[1, j]
                g = gcd(int(u_cand), n)
                if 1 < g < n:
                    p_found = int(g)
                    q_found = n // p_found
                    print(f"\n[!] SUCCESS! Factored n:")
                    print(f"p = {p_found}")
                    print(f"q = {q_found}")
                    
                    # Decrypt flag:
                    phi = (p_found - 1) * (q_found - 1)
                    d_priv = pow(e, -1, phi)
                    c_cipher = int(text.split('c = ')[1].split('\n')[0])
                    m_dec = pow(c_cipher, d_priv, n)
                    flag = long_to_bytes(int(m_dec))
                    print(f"\n==========================================")
                    print(f"[+] FLAG: {flag.decode('utf-8', errors='ignore')}")
                    print(f"==========================================\n")
                    with open('flag.txt', 'wb') as f_out:
                        f_out.write(flag)
                    print(f"[+] Flag written to flag.txt!")
                    exit(0)
