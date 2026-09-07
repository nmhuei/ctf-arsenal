load('test_clean_50_toy.sage')

# Compute K_01, K_02, K_12 on toy:
K01 = vector(ZZ, [ZZ((L[i, 1]*H[0] - L[i, 0]*H[1]) / n) for i in range(3)])
K02 = vector(ZZ, [ZZ((L[i, 2]*H[0] - L[i, 0]*H[2]) / n) for i in range(3)])
K12 = vector(ZZ, [ZZ((L[i, 2]*H[1] - L[i, 1]*H[2]) / n) for i in range(3)])

print("K01 . c == 0:", K01 * c == 0)
print("K02 . c == 0:", K02 * c == 0)
print("K12 . c == 0:", K12 * c == 0)

d = vector(ZZ, [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]])
d12, d02_neg, d01 = d[0], d[1], d[2]
d02 = -d02_neg

print("Delta_01:", d01)
print("- (K01 . w) / 2:", - (K01 * w) / 2)
print("Delta_02:", d02)
print("- (K02 . w) / 2:", - (K02 * w) / 2)
print("Delta_12:", d12)
print("- (K12 . w) / 2:", - (K12 * w) / 2)

print("K01 . u == -d01:", K01 * u == -d01)
print("K02 . u == -d02:", K02 * u == -d02)
print("K12 . u == -d12:", K12 * u == -d12)
