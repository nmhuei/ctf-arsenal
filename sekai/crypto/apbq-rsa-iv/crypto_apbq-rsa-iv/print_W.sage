load('print_T_mat.sage')

# W1, W2 from test_cross_Kc_W.sage:
W1 = vector(ZZ, [x // n for x in v1 * T_mat.transpose()])
W2 = vector(ZZ, [x // n for x in v2 * T_mat.transpose()])

print("W1:", W1)
print("W2:", W2)
print("W1 bits:", [abs(x).bit_length() for x in W1])
print("W2 bits:", [abs(x).bit_length() for x in W2])
print("W1 x W2 == Kc:", W1.cross_product(W2) == Kc)
