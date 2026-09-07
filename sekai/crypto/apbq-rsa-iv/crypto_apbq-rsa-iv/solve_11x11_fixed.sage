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

def quad_form_to_vec(M_form):
    return vector(ZZ, [
        M_form[0, 0],
        M_form[1, 1],
        M_form[2, 2],
        2 * M_form[0, 1],
        2 * M_form[0, 2],
        2 * M_form[1, 2]
    ])

L_col0 = vector(ZZ, [L[i, 0] for i in range(3)])
L_col1 = vector(ZZ, [L[i, 1] for i in range(3)])
L_col2 = vector(ZZ, [L[i, 2] for i in range(3)])

vec_L0 = quad_form_to_vec(Matrix(ZZ, [[L_col0[i]*L_col0[j] for j in range(3)] for i in range(3)]))
vec_L1 = quad_form_to_vec(Matrix(ZZ, [[L_col1[i]*L_col1[j] for j in range(3)] for i in range(3)]))
vec_L2 = quad_form_to_vec(Matrix(ZZ, [[L_col2[i]*L_col2[j] for j in range(3)] for i in range(3)]))

def rank1_to_vec(vA, vB):
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

inv_h1h2 = pow(int(h1 * h2), -1, h0)
coeff0 = (n^2 * inv_h1h2) % h0
vec_h0 = vector(ZZ, [(vec_L0[i] - coeff0 * ZZ(vec_K01_K02[i])) % h0 for i in range(6)])

inv_h0h2 = pow(int(h0 * h2), -1, h1)
coeff1 = (n^2 * inv_h0h2) % h1
vec_h1 = vector(ZZ, [(vec_L1[i] + coeff1 * ZZ(vec_K01_K12[i])) % h1 for i in range(6)])

inv_h0h1 = pow(int(h0 * h1), -1, h2)
coeff2 = (n^2 * inv_h0h1) % h2
vec_h2 = vector(ZZ, [(vec_L2[i] - coeff2 * ZZ(vec_K02_K12[i])) % h2 for i in range(6)])

vec_kn = quad_form_to_vec(Matrix(ZZ, [[ks[i]*ks[j] for j in range(3)] for i in range(3)]))
vec_n = vector(ZZ, [vec_kn[i] % n for i in range(6)])

print("[+] Four modular vectors ready (without factor of 4)!")

X_bound = 1 << 572
S = 1 << 600

M_11 = Matrix(ZZ, 11, 11)

for i in range(6):
    M_11[i, 0] = vec_h0[i] * S
    M_11[i, 1] = vec_h1[i] * S
    M_11[i, 2] = vec_h2[i] * S
    M_11[i, 3] = vec_n[i] * S
    M_11[i, 4 + i] = 1

M_11[6, 3] = -1 * S
M_11[6, 10] = X_bound

M_11[7, 0] = h0 * S
M_11[8, 1] = h1 * S
M_11[9, 2] = h2 * S
M_11[10, 3] = n * S

print(f"Matrix shape: {M_11.dimensions()}")
t0 = time.time()
L_11 = M_11.LLL()
print(f"LLL completed in {time.time() - t0:.3f}s!")

for idx, r in enumerate(L_11.rows()):
    norm_bits = vector(r).norm().n().log(2)
    cand_const = r[10] // X_bound
    print(f"\nRow {idx}: norm bits = {norm_bits:.1f}, const = {cand_const}")
    if abs(cand_const) == 1:
        cand_x = [cand_const * r[4 + i] for i in range(6)]
        print(f"  cand_x bits: {[abs(x).bit_length() for x in cand_x]}")
        if all(x >= 0 and isqrt(x)^2 == x for x in cand_x[:3]):
            w0_cand = isqrt(cand_x[0])
            w1_cand = isqrt(cand_x[1])
            w2_cand = isqrt(cand_x[2])
            print(f"[!] CANDIDATE w = ({w0_cand}, {w1_cand}, {w2_cand})")
            if (w0_cand, w1_cand, w2_cand) == (abs(c[0]), abs(c[1]), abs(c[2])):
                print("  -> This is the TRIVIAL solution w = c!")
            else:
                print("[!] NON-TRIVIAL SOLUTION FOUND!")
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
