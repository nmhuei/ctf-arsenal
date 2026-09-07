set_random_seed(42)

p_bits = 100
B_bits = 60

p = random_prime(2^p_bits, lbound=2^(p_bits-1))
q = random_prime(2^p_bits, lbound=2^(p_bits-1))
n = p * q
B = 1 << B_bits

a = [randint(1, B) for _ in range(3)]
b = [randint(1, B) for _ in range(3)]
h = [a[i] * p + b[i] * q for i in range(3)]

M = Matrix(ZZ, [[h[0], h[1], h[2]], [n, 0, 0], [0, n, 0], [0, 0, n]])
L = Matrix(ZZ, [r for r in M.hermite_form().rows() if vector(r).norm() > 0]).LLL()

ker_h = Matrix(ZZ, [h]).right_kernel().basis_matrix().LLL()
v1, v2 = ker_h[0], ker_h[1]
if v1.cross_product(v2) != vector(ZZ, h):
    if v1.cross_product(v2) == -vector(ZZ, h):
        v2 = -v2

z1 = vector(ZZ, [x // n for x in L * v1])
z2 = vector(ZZ, [x // n for x in L * v2])
c = z1.cross_product(z2)

M_eq = Matrix(ZZ, [
    [0, -c[2], c[1], -z1[0], -z2[0]],
    [c[2], 0, -c[0], -z1[1], -z2[1]],
    [-c[1], c[0], 0, -z1[2], -z2[2]]
])
ker_M = M_eq.right_kernel().basis_matrix().LLL()
R0 = vector(ZZ, ker_M[0][:3])
R1 = vector(ZZ, ker_M[1][:3])
R2 = vector(ZZ, ker_M[2][:3])

c_vec = vector(ZZ, list(c) + [0, 0])
coords_c = ker_M.solve_left(vector(QQ, c_vec))
Kc = vector(ZZ, coords_c)

T0 = R0 * L
T1 = R1 * L
T2 = R2 * L
T_mat = Matrix(ZZ, [list(T0), list(T1), list(T2)])

W1 = vector(ZZ, [x // n for x in v1 * T_mat.transpose()])
W2 = vector(ZZ, [x // n for x in v2 * T_mat.transpose()])

print('W1 x W2 == Kc:', W1.cross_product(W2) == Kc)

k_true = vector(ZZ, [ZZ(x) for x in T_mat.solve_left(vector(QQ, [p * x for x in a]))])
print('k_true:', k_true)

lam_true = W2 * k_true
mu_true = - W1 * k_true

MK = Kc * Kc
EW = W1 * W1
FW = W1 * W2
GW = W2 * W2
Kdot = k_true * Kc

quad_val = EW * lam_true^2 + 2 * FW * lam_true * mu_true + GW * mu_true^2
print('quad_val == MK * norm(k)^2 - Kdot^2:', quad_val == MK * (k_true * k_true) - Kdot^2)
print('quad_val + Kdot^2 % MK == 0:', (quad_val + Kdot^2) % MK == 0)

E1 = Kc.cross_product(W1)
E2 = Kc.cross_product(W2)

print('Kdot * Kc[0] + lam * E1[0] + mu * E2[0] % MK == 0:', (Kdot * Kc[0] + lam_true * E1[0] + mu_true * E2[0]) % MK == 0)

inv_Kc0 = pow(int(Kc[0]), -1, MK)
Kdot_mod_MK = (- inv_Kc0 * (lam_true * E1[0] + mu_true * E2[0])) % MK
print('Kdot % MK == Kdot_mod_MK:', Kdot % MK == Kdot_mod_MK)

coeff_lam2 = (EW + inv_Kc0^2 * E1[0]^2) % MK
coeff_lam_mu = (2 * FW + 2 * inv_Kc0^2 * E1[0] * E2[0]) % MK
coeff_mu2 = (GW + inv_Kc0^2 * E2[0]^2) % MK

Q_K_val = (coeff_lam2 * lam_true^2 + coeff_lam_mu * lam_true * mu_true + coeff_mu2 * mu_true^2) % MK
print('Q_K(Y) % MK == 0:', Q_K_val == 0)
