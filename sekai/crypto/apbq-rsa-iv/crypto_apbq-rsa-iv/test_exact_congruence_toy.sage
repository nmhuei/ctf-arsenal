load('test_check_congruences_toy.sage')

# Test on toy:
# Make sure gcd(h[1]*h[2], h[0]) == 1:
print("gcd(h1*h2, h0):", gcd(h[1]*h[2], h[0]))
if gcd(h[1]*h[2], h[0]) == 1:
    inv_h1h2 = pow(int(h[1]*h[2]), -1, h[0])
    
    # Check:
    # wL[0]^2 - n^2 * inv_h1h2 * (K01 * w) * (K02 * w) == 0 mod h0:
    val0 = (wL[0]^2 - n^2 * inv_h1h2 * (K01 * w) * (K02 * w)) % h[0]
    print("val0 == 0 mod h0:", val0 == 0)

    # Let's check with A0 directly:
    # 4 * n * A0 = H[0]^2 - wL[0]^2
    print("4 * n * A0 == H0^2 - wL0^2:", 4 * n * (a[0]*b[0]) == H[0]^2 - wL[0]^2)
    # A0 mod h0:
    print("A0 == - n * inv_h1h2 * d01 * d02 mod h0:", (a[0]*b[0]) % h[0] == (- n * inv_h1h2 * d01 * d02) % h[0])
