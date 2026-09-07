import time
from Crypto.Util.number import long_to_bytes

t_start = time.time()
print("[*] Loading real challenge parameters...")
with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

# 1. Public lattice Lambda in Z^3:
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

K01 = vector(ZZ, [ZZ((L[i, 1]*H[0] - L[i, 0]*H[1]) / n) for i in range(3)])
K02 = vector(ZZ, [ZZ((L[i, 2]*H[0] - L[i, 0]*H[2]) / n) for i in range(3)])
K12 = vector(ZZ, [ZZ((L[i, 2]*H[1] - L[i, 1]*H[2]) / n) for i in range(3)])

# Monomials of x: [w0^2, w1^2, w2^2, w0*w1, w0*w2, w1*w2]
# Function to convert quadratic form in w to vector on monomials:
def quad_form_to_vec(M_form):
    # M_form is symmetric 3x3 matrix such that w * M_form * w^T is the quadratic form
    return vector(ZZ, [
        M_form[0, 0],
        M_form[1, 1],
        M_form[2, 2],
        2 * M_form[0, 1],
        2 * M_form[0, 2],
        2 * M_form[1, 2]
    ])

# 1. Form for (w . L)_j^2:
# (w . L)_j = w0 * L[0, j] + w1 * L[1, j] + w2 * L[2, j]
# Outer product of column j of L:
L_col0 = vector(ZZ, [L[i, 0] for i in range(3)])
L_col1 = vector(ZZ, [L[i, 1] for i in range(3)])
L_col2 = vector(ZZ, [L[i, 2] for i in range(3)])

vec_L0 = quad_form_to_vec(Matrix(ZZ, [[L_col0[i]*L_col0[j] for j in range(3)] for i in range(3)]))
vec_L1 = quad_form_to_vec(Matrix(ZZ, [[L_col1[i]*L_col1[j] for j in range(3)] for i in range(3)]))
vec_L2 = quad_form_to_vec(Matrix(ZZ, [[L_col2[i]*L_col2[j] for j in range(3)] for i in range(3)]))

# 2. Form for (K_A . w) * (K_B . w):
def rank1_to_vec(vA, vB):
    # (vA . w) * (vB . w)
    M_sym = Matrix(QQ, 3, 3)
    for i in range(3):
        for j in range(3):
            M_sym[i, j] = (vA[i]*vB[j] + vA[j]*vB[i]) / 2
    return vector(QQ, [
        M_sym[0, 0],
        M_sym[1, 1],
        M_sym[2, 2],
        2 * M_sym[0, 1],
        2 * M_sym[0, 2],
        2 * M_sym[1, 2]
    ])

vec_K01_K02 = rank1_to_vec(K01, K02)
vec_K01_K12 = rank1_to_vec(K01, K12)
vec_K02_K12 = rank1_to_vec(K02, K12)

# Modulo relations:
# Modulo h0:
# vec_L0 . x - n^2 * inv_h1h2 / 4 * (vec_K01_K02 . x) = 0 mod h0
inv_h1h2 = pow(int(h1 * h2), -1, h0)
coeff0 = (n^2 * inv_h1h2 * pow(4, -1, h0)) % h0
vec_h0 = vector(ZZ, [(vec_L0[i] - coeff0 * ZZ(vec_K01_K02[i])) % h0 for i in range(6)])

# Modulo h1:
inv_h0h2 = pow(int(h0 * h2), -1, h1)
coeff1 = (n^2 * inv_h0h2 * pow(4, -1, h1)) % h1
vec_h1 = vector(ZZ, [(vec_L1[i] + coeff1 * ZZ(vec_K01_K12[i])) % h1 for i in range(6)])

# Modulo h2:
inv_h0h1 = pow(int(h0 * h1), -1, h2)
coeff2 = (n^2 * inv_h0h1 * pow(4, -1, h2)) % h2
vec_h2 = vector(ZZ, [(vec_L2[i] - coeff2 * ZZ(vec_K02_K12[i])) % h2 for i in range(6)])

# Modulo n:
# (k0*w0 + k1*w1 + k2*w2)^2 - 1 = 0 mod n
vec_kn = quad_form_to_vec(Matrix(ZZ, [[ks[i]*ks[j] for j in range(3)] for i in range(3)]))
vec_n = vector(ZZ, [vec_kn[i] % n for i in range(6)])

print("[+] Four congruence vectors constructed!")
print("vec_h0:", [x.bit_length() for x in vec_h0])
print("vec_h1:", [x.bit_length() for x in vec_h1])
print("vec_h2:", [x.bit_length() for x in vec_h2])
print("vec_n:", [x.bit_length() for x in vec_n])

# Combine vec_h0, vec_h1, vec_h2 into single CRT vector mod H_prod:
H_prod = h0 * h1 * h2
crt0 = (H_prod // h0) * pow(int(H_prod // h0), -1, h0)
crt1 = (H_prod // h1) * pow(int(H_prod // h1), -1, h1)
crt2 = (H_prod // h2) * pow(int(H_prod // h2), -1, h2)

vec_H = vector(ZZ, [(crt0 * vec_h0[i] + crt1 * vec_h1[i] + crt2 * vec_h2[i]) % H_prod for i in range(6)])

# Now combine with vec_n mod n:
M_total = H_prod * n
crt_H = n * pow(int(n), -1, H_prod)
crt_n = H_prod * pow(int(H_prod), -1, n)

# Target:
# vec_H . x = 0 mod H_prod
# vec_n . x = 1 mod n
# So vec_M . x = C mod M_total
# where C = crt_n * 1 mod M_total:
vec_M = vector(ZZ, [(crt_H * vec_H[i] + crt_n * vec_n[i]) % M_total for i in range(6)])
C_val = crt_n % M_total

print(f"M_total bit length: {M_total.bit_length()}")
print(f"C_val bit length: {C_val.bit_length()}")

# Kannan embedding on 6 variables x0..x5 and 1:
# Variables: x0..x5 <= X_bound
# Relation: sum(vec_M[i] * x[i]) - C_val = 0 mod M_total
X_bound = 1 << 572
scale = 1 << (M_total.bit_length() - X_bound.bit_length())

M_kan = Matrix(ZZ, 8, 8)
M_kan[0, 0] = M_total
for i in range(6):
    M_kan[1 + i, 0] = vec_M[i]
    M_kan[1 + i, 1 + i] = X_bound
M_kan[7, 0] = -C_val
M_kan[7, 7] = X_bound

print(f"Matrix shape: {M_kan.dimensions()}")
t0 = time.time()
L_kan = M_kan.LLL()
print(f"LLL completed in {time.time() - t0:.3f}s!")

for idx, r in enumerate(L_kan.rows()):
    if vector(r).norm() == 0: continue
    print(f"Row {idx}: norm bits = {vector(r).norm().n().log(2):.1f}")
    cand_const = r[7] // X_bound
    if abs(cand_const) == 1:
        print(f"[!] FOUND VECTOR WITH CONSTANT +-1! sign = {cand_const}")
        cand_x = [cand_const * (r[1 + i] // X_bound) for i in range(6)]
        print("cand_x bits:", [abs(x).bit_length() for x in cand_x])
        print("cand_x:", cand_x)
        # Verify sqrt of x0, x1, x2:
        if all(x >= 0 and isqrt(x)^2 == x for x in cand_x[:3]):
            w0_cand = isqrt(cand_x[0])
            w1_cand = isqrt(cand_x[1])
            w2_cand = isqrt(cand_x[2])
            print(f"[!] PERFECT SQUARES! w = ({w0_cand}, {w1_cand}, {w2_cand})")
            
            # Check signs and factor n:
            for s0 in [1, -1]:
                for s1 in [1, -1]:
                    for s2 in [1, -1]:
                        w_test = vector(ZZ, [s0*w0_cand, s1*w1_cand, s2*w2_cand])
                        J_val = (ks[0]*w_test[0] + ks[1]*w_test[1] + ks[2]*w_test[2]) % n
                        for diff in [1, -1]:
                            g = gcd(J_val + diff, n)
                            if 1 < g < n:
                                print(f"[!] FACTORED N! p = {g}")
                                q_val = n // g
                                print(f"p = {g}")
                                print(f"q = {q_val}")
                                phi = (g - 1) * (q_val - 1)
                                d_key = pow(e, -1, phi)
                                flag = long_to_bytes(pow(ct, d_key, n))
                                print(f"[!] FLAG: {flag}")
                                with open('FLAG.txt', 'wb') as out_f:
                                    out_f.write(flag)
                                exit(0)
