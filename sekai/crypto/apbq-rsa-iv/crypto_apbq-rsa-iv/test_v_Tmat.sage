load('test_T_mat.sage')

v1_vec = vector(ZZ, v1)
v2_vec = vector(ZZ, v2)

prod1 = v1_vec * T_mat.transpose()
prod2 = v2_vec * T_mat.transpose()

print("v1 * T_mat^T % n == 0:", [x % n == 0 for x in prod1])
print("v2 * T_mat^T % n == 0:", [x % n == 0 for x in prod2])

if all(x % n == 0 for x in prod1) and all(x % n == 0 for x in prod2):
    W1 = vector(ZZ, [x // n for x in prod1])
    W2 = vector(ZZ, [x // n for x in prod2])
    print("W1:", W1)
    print("W2:", W2)
    print("W1 bit lengths:", [abs(x).bit_length() for x in W1])
    print("W2 bit lengths:", [abs(x).bit_length() for x in W2])
