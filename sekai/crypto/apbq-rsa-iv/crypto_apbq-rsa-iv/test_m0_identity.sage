# Let's test if w x c = -(lam * z1 + mu * z2) determines lam and mu as linear forms in w!
# w x c is a linear function of w!
# Can lam and mu be expressed as linear forms in w?
# Let's test symbolically in QQ:

R.<w0, w1, w2, c0, c1, c2, z10, z11, z12, z20, z21, z22> = QQ[]

w = vector(R, [w0, w1, w2])
c = vector(R, [c0, c1, c2])
z1 = vector(R, [z10, z11, z12])
z2 = vector(R, [z20, z21, z22])

# w x c:
wc = vector(R, [
    w1*c2 - w2*c1,
    w2*c0 - w0*c2,
    w0*c1 - w1*c0
])

# If wc = -(lam * z1 + mu * z2),
# then dot with z1 x z2:
# wc . (z1 x z2) = 0!
# And:
# wc x z2 = - lam (z1 x z2)
# So lam = - (wc x z2) / (z1 x z2) (if z1 x z2 != 0)!

z1_x_z2 = vector(R, [
    z1[1]*z2[2] - z1[2]*z2[1],
    z1[2]*z2[0] - z1[0]*z2[2],
    z1[0]*z2[1] - z1[1]*z2[0]
])

denom = z1_x_z2.norm()^2 # or dot with something
# Dot wc x z2 with z1 x z2:
num_lam = - (wc.cross_product(z2)).dot_product(z1_x_z2)
den_lam = z1_x_z2.dot_product(z1_x_z2)

print("Numerator of lam is linear in w:", num_lam.total_degree())
# Is lam an integer when w, c, z1, z2 are from the challenge?
