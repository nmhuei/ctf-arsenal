import time
from Crypto.Util.number import long_to_bytes

t0 = time.time()
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

# 2. Build polynomials for degree 3:
R.<x, y> = ZZ[]
monos = [
    x, y,
    x^2, x*y, y^2,
    x^3, x^2*y, x*y^2, y^3
]
n_monos = len(monos)

polys = []
for j in range(3):
    u = x * L[0, j] + y * L[1, j]
    F = u^2 - H[j] * u
    polys.append(F)
    polys.append(x * F)
    polys.append(y * F)

n_polys = len(polys)
print(f"[*] Step 2: Setting up {n_polys} polynomials over {n_monos} monomials...")

B_lin = 1 << 286
weights = [
    B_lin^2, B_lin^2,
    B_lin, B_lin, B_lin,
    1, 1, 1, 1
]

W = 1 << 2100
dim = n_monos + n_polys
M_lat = Matrix(ZZ, dim, dim)
for i in range(n_monos):
    M_lat[i, i] = weights[i]

for i in range(n_polys):
    for j in range(n_monos):
        coeff = polys[i].monomial_coefficient(monos[j]) % n
        M_lat[j, n_monos + i] = coeff * W
    M_lat[n_monos + i, n_monos + i] = n * W

print(f"[*] Step 3: Running LLL reduction on {dim}x{dim} lattice...")
L_res = M_lat.LLL()
print(f"[+] LLL completed in {time.time() - t0:.2f}s!")

p_found = None
q_found = None

for r in L_res.rows():
    if vector(r).norm() == 0: continue
    cand_x = r[0] // weights[0]
    cand_y = r[1] // weights[1]
    if cand_x == 0 and cand_y == 0: continue
    print(f"Candidate: x = {cand_x}, y = {cand_y}")
    
    for j in range(3):
        u_cand = cand_x * L[0, j] + cand_y * L[1, j]
        g = gcd(int(u_cand), n)
        if 1 < g < n:
            p_found = int(g)
            q_found = n // p_found
            print(f"\n[!] SUCCESS! Factored n:")
            print(f"p = {p_found}")
            print(f"q = {q_found}")
            break
    if p_found: break

if p_found:
    print("[*] Step 4: Decrypting RSA ciphertext...")
    phi = (p_found - 1) * (q_found - 1)
    d_priv = pow(e, -1, phi)
    m_dec = pow(c, d_priv, n)
    flag = long_to_bytes(int(m_dec))
    print(f"\n==========================================")
    print(f"[+] FLAG: {flag.decode('utf-8', errors='ignore')}")
    print(f"==========================================\n")
    with open('flag.txt', 'wb') as f_out:
        f_out.write(flag)
    print(f"[+] Flag written to flag.txt!")
else:
    print("[-] Degree 3 didn't find factor directly, let's inspect L_res norms...")
    for idx in range(min(5, len(L_res.rows()))):
        r = L_res.rows()[idx]
        print(f"Row {idx}: norm bits = {vector(r).norm().n().log(2):.1f}")
