with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

M_ker = Matrix(ZZ, [list(hints)]).right_kernel().basis_matrix().LLL()
v1 = M_ker[0]
v2 = M_ker[1]

print("v1 norm bits:", vector(v1).norm().n().log(2))
print("v2 norm bits:", vector(v2).norm().n().log(2))

# Delta_12 = lam * v1[0] + mu * v2[0]
# Delta_02 = -(lam * v1[1] + mu * v2[1])
# Delta_01 = lam * v1[2] + mu * v2[2]

# Q0 = Delta_01 * Delta_02:
# = (lam * v1[2] + mu * v2[2]) * (- (lam * v1[1] + mu * v2[1]))
# = - v1[2]*v1[1] * lam^2 - (v1[2]*v2[1] + v2[2]*v1[1]) * lam*mu - v2[2]*v2[1] * mu^2

q0_20 = - v1[2] * v1[1]
q0_11 = - (v1[2] * v2[1] + v2[2] * v1[1])
q0_02 = - v2[2] * v2[1]

# Q1 = Delta_01 * Delta_12:
# = (lam * v1[2] + mu * v2[2]) * (lam * v1[0] + mu * v2[0])
q1_20 = v1[2] * v1[0]
q1_11 = v1[2] * v2[0] + v2[2] * v1[0]
q1_02 = v2[2] * v2[0]

# Q2 = Delta_02 * Delta_12:
# = (- (lam * v1[1] + mu * v2[1])) * (lam * v1[0] + mu * v2[0])
q2_20 = - v1[1] * v1[0]
q2_11 = - (v1[1] * v2[0] + v2[1] * v1[0])
q2_02 = - v2[1] * v2[0]

print("Q0 coeffs bits:", [x.bit_length() for x in [q0_20, q0_11, q0_02]])
print("Q1 coeffs bits:", [x.bit_length() for x in [q1_20, q1_11, q1_02]])
print("Q2 coeffs bits:", [x.bit_length() for x in [q2_20, q2_11, q2_02]])

# Modulo relations:
# A0 = - n * (h1 h2)^-1 * Q0(lam, mu) mod h0
# A1 = n * (h0 h2)^-1 * Q1(lam, mu) mod h1
# A2 = - n * (h0 h1)^-1 * Q2(lam, mu) mod h2

inv_h1h2 = pow(int(h1 * h2), -1, h0)
inv_h0h2 = pow(int(h0 * h2), -1, h1)
inv_h0h1 = pow(int(h0 * h1), -1, h2)

c0 = (- n * inv_h1h2) % h0
c1 = (n * inv_h0h2) % h1
c2 = (- n * inv_h0h1) % h2

# row0: c0 * [q0_20, q0_11, q0_02] mod h0
# row1: c1 * [q1_20, q1_11, q1_02] mod h1
# row2: c2 * [q2_20, q2_11, q2_02] mod h2

row0 = [(c0 * x) % h0 for x in [q0_20, q0_11, q0_02]]
row1 = [(c1 * x) % h1 for x in [q1_20, q1_11, q1_02]]
row2 = [(c2 * x) % h2 for x in [q2_20, q2_11, q2_02]]

print("row0:", row0)
print("row1:", row1)
print("row2:", row2)
