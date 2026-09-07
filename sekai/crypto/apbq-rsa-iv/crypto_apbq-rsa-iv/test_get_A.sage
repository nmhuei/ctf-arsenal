load('test_factor_s.sage')

cw = vector(QQ, [
    c[1]*w_dir[2] - c[2]*w_dir[1],
    c[2]*w_dir[0] - c[0]*w_dir[2],
    c[0]*w_dir[1] - c[1]*w_dir[0]
])
M_z = Matrix(QQ, [list(z1), list(z2)])
sol = M_z.solve_left(cw)

# sol = (lam_dir, mu_dir)
lam_dir = 2 * sol[0]
mu_dir = 2 * sol[1]

print("lam_dir bit length:", ZZ(lam_dir).bit_length())
print("mu_dir bit length:", ZZ(mu_dir).bit_length())

d_cand = ZZ(lam_dir) * v1 + ZZ(mu_dir) * v2

d12 = d_cand[0]
d02 = -d_cand[1]
d01 = d_cand[2]

print("d12 bit length:", abs(d12).bit_length())
print("d02 bit length:", abs(d02).bit_length())
print("d01 bit length:", abs(d01).bit_length())

# Remember: d_cand is proportional to true d!
# d_cand = S * d_true.
# Delta_01 * Delta_02 is scaled by S^2!
# And A0 = -n (h1 h2)^-1 Delta_01 Delta_02 mod h0!
# So A0_cand = S^2 * A0_true mod h0!
# What is the ratio between d12, d02, d01 and true d?
# Notice: ||d_true|| <= B^2 = 2^1248!
# What is ||d_cand||?
print("d_cand norm bits:", vector(d_cand).norm().n().log(2))

inv_h1h2 = pow(int(h1 * h2), -1, h0)
inv_h0h2 = pow(int(h0 * h2), -1, h1)
inv_h0h1 = pow(int(h0 * h1), -1, h2)

# d0 = d12, d1 = -d02, d2 = d01
# d_cand = (d0, -d1, d2):
# Note: d_cand = (d12, d02_neg, d01)
# d_cand = (d_cand[0], d_cand[1], d_cand[2])
# d_cand[0] = d12
# d_cand[1] = -d02
# d_cand[2] = d01

d12_val = d_cand[0]
d02_val = -d_cand[1]
d01_val = d_cand[2]

# Delta_01 * Delta_02 = d01 * d02:
# T0 = -n * inv_h1h2 * d01 * d02 mod h0
T0 = (-n * inv_h1h2 * d01_val * d02_val) % h0
T1 = (n * inv_h0h2 * d01_val * d12_val) % h1
T2 = (-n * inv_h0h1 * d02_val * d12_val) % h2

print("T0 bit length:", T0.bit_length(), "vs h0:", h0.bit_length())
print("T1 bit length:", T1.bit_length(), "vs h1:", h1.bit_length())
print("T2 bit length:", T2.bit_length(), "vs h2:", h2.bit_length())
