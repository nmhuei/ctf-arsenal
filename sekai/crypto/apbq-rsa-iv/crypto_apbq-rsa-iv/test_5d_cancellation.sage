load('test_Q_K_mod_MK.sage')

# In synthetic instance:
# a = [a0, a1, a2], b = [b0, b1, b2]
A0_true = a[0] * b[0]
A1_true = a[1] * b[1]
A2_true = a[2] * b[2]

# True lam, mu:
print("True A0, A1, A2 bit lengths:", A0_true.bit_length(), A1_true.bit_length(), A2_true.bit_length())
print("True lam, mu bit lengths:", lam_true.bit_length(), mu_true.bit_length())

# Check the three linear expressions:
# Expr 01: h1^2 * A0 - h0^2 * A1 - h0 * h1 * (lam * v1[2] + mu * v2[2])
expr01 = h[1]^2 * A0_true - h[0]^2 * A1_true - h[0] * h[1] * (lam_true * v1[2] + mu_true * v2[2])
expr02 = h[2]^2 * A0_true - h[0]^2 * A2_true + h[0] * h[2] * (lam_true * v1[1] + mu_true * v2[1])
expr12 = h[2]^2 * A1_true - h[1]^2 * A2_true - h[1] * h[2] * (lam_true * v1[0] + mu_true * v2[0])

print("expr01 bit length:", abs(expr01).bit_length())
print("expr02 bit length:", abs(expr02).bit_length())
print("expr12 bit length:", abs(expr12).bit_length())
print("h0^2 bit length:", (h[0]^2).bit_length())
print("Cancellation bits 01:", (h[0]^2 * A1_true).bit_length() - abs(expr01).bit_length())
