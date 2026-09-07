load('test_v_Tmat.sage')

def cross_prod(u, v):
    return vector(ZZ, [
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    ])

Kc_x_W1 = cross_prod(Kc, W1)
Kc_x_W2 = cross_prod(Kc, W2)
Kc_norm_sq = Kc * Kc

print("Kc norm sq bit length:", Kc_norm_sq.bit_length())
print("Kc x W1 bit lengths:", [abs(x).bit_length() for x in Kc_x_W1])
print("Kc x W2 bit lengths:", [abs(x).bit_length() for x in Kc_x_W2])

# Check orthogonality with Kc:
print("Kc . (Kc x W1) == 0:", Kc * Kc_x_W1 == 0)
print("Kc . (Kc x W2) == 0:", Kc * Kc_x_W2 == 0)

# Check cross product W1 x W2:
W1_x_W2 = cross_prod(W1, W2)
print("W1 x W2 bit lengths:", [abs(x).bit_length() for x in W1_x_W2])
print("Is W1 x W2 parallel to Kc?:", cross_prod(W1_x_W2, Kc) == 0)
if cross_prod(W1_x_W2, Kc) == 0:
    ratio = [W1_x_W2[i] / Kc[i] for i in range(3)]
    print("Ratio (W1 x W2) / Kc:", ratio)
