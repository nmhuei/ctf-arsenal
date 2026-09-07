load('test_K_identity.sage')

# w . L:
wL = w * L

# Check:
inv_h1h2 = pow(int(h[1]*h[2]), -1, h[0])
inv_h0h2 = pow(int(h[0]*h[2]), -1, h[1])
inv_h0h1 = pow(int(h[0]*h[1]), -1, h[2])

val0 = (wL[0]^2 - n^2 * inv_h1h2 * (K01 * w) * (K02 * w) / 4) % h[0]
val1 = (wL[1]^2 + n^2 * inv_h0h2 * (K01 * w) * (K12 * w) / 4) % h[1]
val2 = (wL[2]^2 - n^2 * inv_h0h1 * (K02 * w) * (K12 * w) / 4) % h[2]

print("val0 == 0 mod h0:", val0 == 0)
print("val1 == 0 mod h1:", val1 == 0)
print("val2 == 0 mod h2:", val2 == 0)
