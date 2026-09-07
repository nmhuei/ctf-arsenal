load('test_complement_2d.sage')

# R_i is u-part of Row i of ker_M:
R0 = vector(ZZ, ker_M[0][:3])
R1 = vector(ZZ, ker_M[1][:3])
R2 = vector(ZZ, ker_M[2][:3])

# Check that Kc * R = c:
Kc = vector(ZZ, coords_c)
print("Kc * R == c:", Kc[0]*R0 + Kc[1]*R1 + Kc[2]*R2 == c)

# Compute L-products:
# row vectors in Z^3:
T0 = R0 * L
T1 = R1 * L
T2 = R2 * L

print("T0 norm bits:", vector(T0).norm().n().log(2))
print("T1 norm bits:", vector(T1).norm().n().log(2))
print("T2 norm bits:", vector(T2).norm().n().log(2))

# Check Kc * T == H:
print("Kc * T == H:", Kc[0]*T0 + Kc[1]*T1 + Kc[2]*T2 == H)

# Modulo n:
print("T0 % n:", [x % n for x in T0])
# Ratios with H mod n:
h0_inv = pow(int(h0), -1, n)
for idx, Ti in enumerate([T0, T1, T2]):
    ratio = [(x * pow(int(H[j]), -1, n)) % n for j, x in enumerate(Ti)]
    print(f"T{idx} ratios with H mod n:", ratio)
    print(f"  Are all 3 ratios equal?:", ratio[0] == ratio[1] == ratio[2])
