load('test_identity_sq.sage')
val = 2 * (h[1]^2 * A0 + h[0]^2 * A1) + n * Delta01^2
print('diff_sq // n == 2*(h1^2*A0 + h0^2*A1) + n*Delta01^2:', (diff_sq // n) == val)
