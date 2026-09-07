load('test_alpha_tau.sage')

# P(k0, k1, k2) = (tau0*k0 + tau1*k1 + tau2*k2)^2 - (tau0*k0 + tau1*k1 + tau2*k2) mod n
# We know P(Kc) == 0 mod n!
# Let's test with centered variables delta = 2*k - Kc:
# Then (beta0*d0 + beta1*d1 + beta2*d2)^2 - 1 == 0 mod n!
# Let Q(d0, d1, d2) = (tau0*d0 + tau1*d1 + tau2*d2)^2 - 1 mod n
# At d = Kc: Q(Kc) == 0 mod n.
# At d = -Kc: Q(-Kc) == 0 mod n.
# At d = delta_true: Q(delta_true) == 0 mod n!

# Monomials in delta: d0, d1, d2, d0^2, d1^2, d2^2, d0*d1, d0*d2, d1*d2, 1
# Delta bounds: D = 2^192

D = 1 << 192

# Let's check determinant of the lattice for degree 2 on delta:
# Polynomials:
# 1. Q(d) = (sum tau_i d_i)^2 - 1 (vanishes mod n)
# 2. n * d_i * d_j (6 polys)
# 3. n * d_i (3 polys)
# 4. n * 1 (1 poly)
# Total 11 polynomials, 10 monomials!
# Let's test in Sage:

R.<d0, d1, d2> = PolynomialRing(ZZ)
Q_poly = (tau0*d0 + tau1*d1 + tau2*d2)^2 - 1

monos = [1, d0, d1, d2, d0^2, d1^2, d2^2, d0*d1, d0*d2, d1*d2]
polys = [Q_poly]
for m in monos:
    if m != 1 and m.degree() == 2:
        polys.append(n * m)

print("Number of polys:", len(polys))
print("Number of monos:", len(monos))
