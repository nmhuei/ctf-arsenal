with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

M_ker = Matrix(ZZ, [hints]).right_kernel().basis_matrix().LLL()
v1 = M_ker[0]
v2 = M_ker[1]

# Delta_12 = lam*v1[0] + mu*v2[0]
# Delta_02 = -(lam*v1[1] + mu*v2[1])
# Delta_01 = lam*v1[2] + mu*v2[2]

# Let u = lam^2, v = lam*mu, w = mu^2.
# Delta_01^2 = v1[2]^2 * u + 2*v1[2]*v2[2] * v + v2[2]^2 * w
# Delta_02^2 = v1[1]^2 * u + 2*v1[1]*v2[1] * v + v2[1]^2 * w
# Delta_12^2 = v1[0]^2 * u + 2*v1[0]*v2[0] * v + v2[0]^2 * w

# Eq 1:
# h2*v1[0]*v1[1]*Delta_01^2 + h1*v1[0]*v1[2]*Delta_02^2 + h0*v1[1]*v1[2]*Delta_12^2 + w*h0*h1*h2 = 0
coeff1_u = h2*v1[0]*v1[1]*v1[2]^2 + h1*v1[0]*v1[2]*v1[1]^2 + h0*v1[1]*v1[2]*v1[0]^2
coeff1_v = h2*v1[0]*v1[1]*(2*v1[2]*v2[2]) + h1*v1[0]*v1[2]*(2*v1[1]*v2[1]) + h0*v1[1]*v1[2]*(2*v1[0]*v2[0])
coeff1_w = h2*v1[0]*v1[1]*v2[2]^2 + h1*v1[0]*v1[2]*v2[1]^2 + h0*v1[1]*v1[2]*v2[0]^2 + h0*h1*h2

print("Eq 1 coefficients:")
print("coeff1_u:", coeff1_u)
print("coeff1_v:", coeff1_v)
print("coeff1_w:", coeff1_w)

# Eq 2:
# h2*v2[0]*v2[1]*Delta_01^2 + h1*v2[0]*v2[2]*Delta_02^2 + h0*v2[1]*v2[2]*Delta_12^2 + u*h0*h1*h2 = 0
coeff2_u = h2*v2[0]*v2[1]*v1[2]^2 + h1*v2[0]*v2[2]*v1[1]^2 + h0*v2[1]*v2[2]*v1[0]^2 + h0*h1*h2
coeff2_v = h2*v2[0]*v2[1]*(2*v1[2]*v2[2]) + h1*v2[0]*v2[2]*(2*v1[1]*v2[1]) + h0*v2[1]*v2[2]*(2*v1[0]*v2[0])
coeff2_w = h2*v2[0]*v2[1]*v2[2]^2 + h1*v2[0]*v2[2]*v2[1]^2 + h0*v2[1]*v2[2]*v2[0]^2

print("\nEq 2 coefficients:")
print("coeff2_u:", coeff2_u)
print("coeff2_v:", coeff2_v)
print("coeff2_w:", coeff2_w)
