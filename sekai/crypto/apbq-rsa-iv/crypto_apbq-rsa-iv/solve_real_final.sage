import time
from Crypto.Util.number import long_to_bytes

t0 = time.time()
print("[*] Loading challenge parameters...")
with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

# 1. Build lattice Lambda = < H, n*e0, n*e1, n*e2 >
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
print(f"[+] Lattice reduced! c bit lengths: {[abs(x).bit_length() for x in c]}")

# 2. Setup the 3 quadratic equations in (x, y):
# For j in {0, 1, 2}:
# (x*L[0,j] + y*L[1,j])^2 - H[j]*(x*L[0,j] + y*L[1,j]) = 0 mod n
# Variables: x, y, X=x^2, Y=x*y, Z=y^2
eqs = []
for j in range(3):
    L0j = L[0, j]
    L1j = L[1, j]
    Hj = H[j]

    a_x = (-Hj * L0j) % n
    a_y = (-Hj * L1j) % n
    a_X = (L0j^2) % n
    a_Y = (2 * L0j * L1j) % n
    a_Z = (L1j^2) % n
    eqs.append((a_x, a_y, a_X, a_Y, a_Z))

# Max bounds:
B_lin = 1 << 290
B_quad = 1 << 580

# 3. Build 8x8 Coppersmith lattice
print("[*] Step 2: Building 8x8 Coppersmith lattice...")
W = 1 << 2050
M_lat = Matrix(ZZ, 8, 8)
M_lat[0, 0] = B_lin
M_lat[1, 1] = B_lin
M_lat[2, 2] = 1
M_lat[3, 3] = 1
M_lat[4, 4] = 1

for j in range(3):
    M_lat[0, 5 + j] = eqs[j][0] * W
    M_lat[1, 5 + j] = eqs[j][1] * W
    M_lat[2, 5 + j] = eqs[j][2] * W
    M_lat[3, 5 + j] = eqs[j][3] * W
    M_lat[4, 5 + j] = eqs[j][4] * W
    M_lat[5 + j, 5 + j] = n * W

print("[*] Step 3: Running LLL reduction...")
L_res = M_lat.LLL()
print(f"[+] LLL completed in {time.time() - t0:.2f}s!")

p_found = None
q_found = None

for r in L_res.rows():
    if vector(r).norm() == 0: continue
    cand_x = r[0] // B_lin
    cand_y = r[1] // B_lin
    if cand_x == 0 and cand_y == 0: continue
    
    for j in range(3):
        u_cand = cand_x * L[0, j] + cand_y * L[1, j]
        g = gcd(int(u_cand), n)
        if 1 < g < n:
            p_found = int(g)
            q_found = n // p_found
            print(f"[!] SUCCESS! Factored n:")
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
    print("[-] Failed to find factor with current weights.")
