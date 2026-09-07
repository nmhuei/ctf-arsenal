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
print(f"[+] Reduced basis found! c = {c}")

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

print("[+] Linear forms modulo h0, h1, h2 constructed!")

# CRT combine the 3 modular relations:
H_prod = h0 * h1 * h2
V_crt = []
for i in range(6):
    r_i = crt([int(vec0[i]), int(vec1[i]), int(vec2[i])], [int(h0), int(h1), int(h2)])
    V_crt.append(ZZ(r_i))
V_crt = vector(ZZ, V_crt)

print(f"[+] CRT vector constructed! H_prod bit length = {H_prod.bit_length()}")

# Bounds on x:
W0 = 1 << (abs(c[0]).bit_length() + 1)
W1 = 1 << (abs(c[1]).bit_length() + 1)
W2 = 1 << (abs(c[2]).bit_length() + 1)

X_bounds = [
    W0^2,
    W1^2,
    W2^2,
    W0 * W1,
    W0 * W2,
    W1 * W2
]

X_max = max(X_bounds)
weights = [X_max // X_bounds[i] for i in range(6)]

# Build 7x7 lattice for V_crt . x = 0 mod H_prod:
# [ K * V_crt[0]  weights[0]  0  0  0  0  0 ]
# [ K * V_crt[1]      0   weights[1] 0  0  0  0 ]
# ...
# [ K * H_prod        0       0  0  0  0  0 ]
K_fac = (1 << 6000)
M_lat = Matrix(ZZ, 7, 7)
for i in range(6):
    M_lat[i, 0] = K_fac * V_crt[i]
    M_lat[i, 1 + i] = weights[i]
M_lat[6, 0] = K_fac * H_prod

print("[*] Running LLL on 7x7 lattice...")
t_lll = time.time()
L_red = M_lat.LLL()
print(f"[+] LLL completed in {time.time() - t_lll:.3f}s!")

ks = [(L[i][0] * pow(int(h0), -1, n)) % n for i in range(3)]

for idx, r in enumerate(L_red.rows()):
    if vector(r).norm() == 0: continue
    x_cand = [r[1 + i] // weights[i] for i in range(6)]
    norm_x = vector(ZZ, x_cand).norm().n()
    print(f"Row {idx}: norm bits = {norm_x.log(2):.1f}")
    if norm_x == 0: continue
    
    # Check if x_cand can give w:
    # x0 = w0^2, x1 = w1^2, x2 = w2^2
    print(f"  cand: {x_cand}")
    if x_cand[0] >= 0 and x_cand[1] >= 0 and x_cand[2] >= 0:
        w0_cand = ZZ(round(sqrt(RR(x_cand[0]))))
        w1_cand = ZZ(round(sqrt(RR(x_cand[1]))))
        w2_cand = ZZ(round(sqrt(RR(x_cand[2]))))
        
        # Test sign combinations:
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
