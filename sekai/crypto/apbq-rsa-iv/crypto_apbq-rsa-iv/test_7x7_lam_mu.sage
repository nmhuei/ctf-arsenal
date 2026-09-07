load('test_cross_Kc_W.sage')

# We have W1, W2 such that:
# lam = W2 . k, mu = -W1 . k
# And d = lam * v1 + mu * v2
# Also d01 = lam * v1[2] + mu * v2[2]
# d02 = -(lam * v1[1] + mu * v2[1])
# d12 = lam * v1[0] + mu * v2[0]

# Delta cross relations:
# Delta_01 = lam * v1[2] + mu * v2[2]
# Delta_02 = -(lam * v1[1] + mu * v2[1])
# Delta_12 = lam * v1[0] + mu * v2[0]

# Coefficients of lam^2, lam*mu, mu^2 in Delta_01 * Delta_02:
# (l*v1[2] + m*v2[2]) * (-l*v1[1] - m*v2[1])
# = - v1[2]*v1[1] * l^2 - (v1[2]*v2[1] + v2[2]*v1[1]) * l*m - v2[2]*v2[1] * m^2
r00 = - v1[2] * v1[1]
r01 = - (v1[2] * v2[1] + v2[2] * v1[1])
r02 = - v2[2] * v2[1]

# Delta_01 * Delta_12:
r10 = v1[2] * v1[0]
r11 = v1[2] * v2[0] + v2[2] * v1[0]
r12 = v2[2] * v2[0]

# Delta_02 * Delta_12:
r20 = - v1[1] * v1[0]
r21 = - (v1[1] * v2[0] + v2[1] * v1[0])
r22 = - v2[1] * v2[0]

# Multipliers:
# A0 = - n * (h1*h2)^-1 * (Delta01 * Delta02) mod h0
inv_h1h2 = pow(int(h1 * h2), -1, h0)
C0 = (- n * inv_h1h2) % h0

inv_h0h2 = pow(int(h0 * h2), -1, h1)
C1 = (n * inv_h0h2) % h1

inv_h0h1 = pow(int(h0 * h1), -1, h2)
C2 = (- n * inv_h0h1) % h2

q0 = [(C0 * x) % h0 for x in [r00, r01, r02]]
q1 = [(C1 * x) % h1 for x in [r10, r11, r12]]
q2 = [(C2 * x) % h2 for x in [r20, r21, r22]]

print("q0:", q0)
print("q1:", q1)
print("q2:", q2)
