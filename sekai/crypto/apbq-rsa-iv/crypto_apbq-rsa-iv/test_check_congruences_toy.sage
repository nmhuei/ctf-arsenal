load('test_K_identity.sage')

# w is true w on toy.
# c is trivial c on toy.

# Let's test P_n:
J_true = (ks[0]*w[0] + ks[1]*w[1] + ks[2]*w[2]) % n
print("J_true^2 mod n == 1:", (J_true^2) % n == 1)

J_triv = (ks[0]*c[0] + ks[1]*c[1] + ks[2]*c[2]) % n
print("J_triv^2 mod n == 1:", (J_triv^2) % n == 1)

# Now test P_0, P_1, P_2:
wL = w * L
cL = c * L

# Real formula:
# H0^2 - wL[0]^2 == 4 * n * A0
# A0 = - n * inv_h1h2 * Delta01 * Delta02 mod h0
# 4 * n * A0 == - 4 * n^2 * inv_h1h2 * Delta01 * Delta02 mod h0
# But Delta01 = - (K01 . w) / 2
# So Delta01 * Delta02 = (K01 . w) * (K02 . w) / 4
# So 4 * n * A0 == - n^2 * inv_h1h2 * (K01 . w) * (K02 . w) mod h0!
# And H0^2 = 0 mod h0!
# So - wL[0]^2 == - n^2 * inv_h1h2 * (K01 . w) * (K02 . w) mod h0!
# wL[0]^2 - n^2 * inv_h1h2 * (K01 . w) * (K02 . w) == 0 mod h0!

# WAIT! LOOK AT THE FACTOR OF 4:
# 4 * n * A0 == - 4 * n^2 * inv_h1h2 * Delta01 * Delta02 mod h0!
# - wL[0]^2 == - 4 * n^2 * inv_h1h2 * (K01 . w / 2) * (K02 . w / 2) mod h0
# = - 4 * n^2 * inv_h1h2 * (1/4) * (K01 . w) * (K02 . w) mod h0
# = - n^2 * inv_h1h2 * (K01 . w) * (K02 . w) mod h0!
# THERE IS NO DIVISION BY 4!
# The 4 in 4 * n * A0 and the 1/4 in (K01.w/2)(K02.w/2) CANCELLED!
# 4 * (1/4) = 1!
