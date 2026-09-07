import time
from Crypto.Util.number import long_to_bytes

t_start = time.time()
print("[*] Loading challenge parameters...")
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

M_ker = Matrix(ZZ, [hints]).right_kernel().basis_matrix().LLL()
v1 = M_ker[0]
v2 = M_ker[1]

z1 = vector(ZZ, [ZZ(x) for x in (2 * L * v1 / n)])
z2 = vector(ZZ, [ZZ(x) for x in (2 * L * v2 / n)])

Y1 = vector(ZZ, [
    c[1]*z1[2] - c[2]*z1[1],
    c[2]*z1[0] - c[0]*z1[2],
    c[0]*z1[1] - c[1]*z1[0]
])

Y2 = vector(ZZ, [
    c[1]*z2[2] - c[2]*z2[1],
    c[2]*z2[0] - c[0]*z2[2],
    c[0]*z2[1] - c[1]*z2[0]
])

Y3 = c
Y = Matrix(ZZ, [list(Y1), list(Y2), list(Y3)]).transpose()
adjY = Y.adjugate()
Delta_z = c * vector(ZZ, [z1[1]*z2[2]-z1[2]*z2[1], z1[2]*z2[0]-z1[0]*z2[2], z1[0]*z2[1]-z1[1]*z2[0]])

m0 = vector(ZZ, [x // Delta_z for x in adjY[0]])
m1 = vector(ZZ, [x // Delta_z for x in adjY[1]])

F12 = v1[0]*m0 + v2[0]*m1
F02 = -(v1[1]*m0 + v2[1]*m1)
F01 = v1[2]*m0 + v2[2]*m1

def quad_to_linear(F_A, F_B):
    return vector(ZZ, [
        F_A[0]*F_B[0],
        F_A[1]*F_B[1],
        F_A[2]*F_B[2],
        F_A[0]*F_B[1] + F_A[1]*F_B[0],
        F_A[0]*F_B[2] + F_A[2]*F_B[0],
        F_A[1]*F_B[2] + F_A[2]*F_B[1]
    ])

G0 = quad_to_linear(F01, F02)
G1 = quad_to_linear(F01, F12)
G2 = quad_to_linear(F02, F12)

L0_quad = vector(ZZ, [
    L[0, 0]^2, L[1, 0]^2, L[2, 0]^2,
    2 * L[0, 0] * L[1, 0], 2 * L[0, 0] * L[2, 0], 2 * L[1, 0] * L[2, 0]
])

L1_quad = vector(ZZ, [
    L[0, 1]^2, L[1, 1]^2, L[2, 1]^2,
    2 * L[0, 1] * L[1, 1], 2 * L[0, 1] * L[2, 1], 2 * L[1, 1] * L[2, 1]
])

L2_quad = vector(ZZ, [
    L[0, 2]^2, L[1, 2]^2, L[2, 2]^2,
    2 * L[0, 2] * L[1, 2], 2 * L[0, 2] * L[2, 2], 2 * L[1, 2] * L[2, 2]
])

inv_h1h2 = pow(int(h1 * h2), -1, h0)
coeff_G0 = (4 * n^2 * inv_h1h2) % h0
vec0 = vector(ZZ, [(L0_quad[i] - coeff_G0 * G0[i]) % h0 for i in range(6)])

inv_h0h2 = pow(int(h0 * h2), -1, h1)
coeff_G1 = (4 * n^2 * inv_h0h2) % h1
vec1 = vector(ZZ, [(L1_quad[i] + coeff_G1 * G1[i]) % h1 for i in range(6)])

inv_h0h1 = pow(int(h0 * h1), -1, h2)
coeff_G2 = (4 * n^2 * inv_h0h1) % h2
vec2 = vector(ZZ, [(L2_quad[i] - coeff_G2 * G2[i]) % h2 for i in range(6)])

# CRT on coordinates 1..5:
H_prod = h0 * h1 * h2
V5_crt = []
for i in range(1, 6):
    r_i = crt([int(vec0[i]), int(vec1[i]), int(vec2[i])], [int(h0), int(h1), int(h2)])
    V5_crt.append(ZZ(r_i))
V5_crt = vector(ZZ, V5_crt)

print(f"[+] 5-variable CRT vector constructed! H_prod bit length = {H_prod.bit_length()}")

W0 = 1 << (abs(c[0]).bit_length() + 1)
W1 = 1 << (abs(c[1]).bit_length() + 1)
W2 = 1 << (abs(c[2]).bit_length() + 1)

# Bounds on (x1, x2, x3, x4, x5):
X5_bounds = [
    W1^2,
    W2^2,
    W0 * W1,
    W0 * W2,
    W1 * W2
]

X_max = max(X5_bounds)
weights = [X_max // X5_bounds[i] for i in range(5)]

# Build 6x6 lattice for V5_crt . x5 = 0 mod H_prod:
# Row i (0..4): [ K * V5_crt[i], 0, ..., weights[i], ... 0 ]
# Row 5:       [ K * H_prod,     0, ..., 0 ]

K_fac = 1 << 6000
M_lat = Matrix(ZZ, 6, 6)
for i in range(5):
    M_lat[i, 0] = K_fac * V5_crt[i]
    M_lat[i, 1 + i] = weights[i]
M_lat[5, 0] = K_fac * H_prod

print("[*] Running LLL on 6x6 lattice...")
t_lll = time.time()
L_red = M_lat.LLL()
print(f"[+] LLL completed in {time.time() - t_lll:.3f}s!")

ks = [(L[i][0] * pow(int(h0), -1, n)) % n for i in range(3)]

for idx, r in enumerate(L_red.rows()):
    if vector(r).norm() == 0: continue
    # Extract x5_cand:
    x5_cand = [r[1 + i] // weights[i] for i in range(5)]
    norm_x = vector(ZZ, x5_cand).norm().n()
    print(f"Row {idx}: norm bits = {norm_x.log(2):.1f}")
    if norm_x == 0: continue
    
    # x1 = w1^2, x2 = w2^2, x3 = w0*w1, x4 = w0*w2, x5 = w1*w2
    x1, x2, x3, x4, x5 = x5_cand
    print(f"  x1: {x1.bit_length()} bits, x2: {x2.bit_length()} bits")
    
    # Check if x1 >= 0 and x2 >= 0:
    for sign_flip in [1, -1]:
        x1_s = sign_flip * x1
        x2_s = sign_flip * x2
        x3_s = sign_flip * x3
        x4_s = sign_flip * x4
        x5_s = sign_flip * x5
        
        if x1_s > 0 and x2_s > 0:
            w1_cand = ZZ(round(sqrt(RR(x1_s))))
            w2_cand = ZZ(round(sqrt(RR(x2_s))))
            
            # w0 = x3 / w1
            if w1_cand > 0:
                w0_cand = x3_s // w1_cand
                for s0 in [1, -1]:
                    for s1 in [1, -1]:
                        for s2 in [1, -1]:
                            w_test = (s0 * w0_cand, s1 * w1_cand, s2 * w2_cand)
                            J = (ks[0]*w_test[0] + ks[1]*w_test[1] + ks[2]*w_test[2]) % n
                            p_cand = gcd(J - 1, n)
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
