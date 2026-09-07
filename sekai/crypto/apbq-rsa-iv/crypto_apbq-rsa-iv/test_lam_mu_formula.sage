load('test_check_cxw_toy.sage')

# z1 = (L * v1) / n
# z2 = (L * v2) / n
z1_vec = vector(ZZ, [x // n for x in L * v1])
z2_vec = vector(ZZ, [x // n for x in L * v2])

print("z1 x z2 == c:", cross_prod(z1_vec, z2_vec) == c)

lam_formula = - (u * z2_vec)
mu_formula = u * z1_vec

print(f"lam true = {lam_val}, lam formula = {lam_formula}")
print(f"mu true = {mu_val}, mu formula = {mu_formula}")
print("Formula matches lam?", lam_val == lam_formula)
print("Formula matches mu?", mu_val == mu_formula)
