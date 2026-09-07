load('test_K_diff_gcd.sage')
diff_sq = (h[0] * h[1])^2 - K_diff^2
print('diff_sq == n * Delta01^2:', diff_sq == n * Delta01^2)
print('diff_sq bit length:', diff_sq.bit_length())
print('n * Delta01^2 bit length:', (n * Delta01^2).bit_length())
