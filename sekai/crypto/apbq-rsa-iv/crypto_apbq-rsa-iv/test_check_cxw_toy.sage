load('test_K_identity.sage')

# On toy example:
# v1, v2 are basis of right_kernel of h
M_ker = Matrix(ZZ, [list(h)]).right_kernel().basis_matrix().LLL()
v1 = M_ker[0]
v2 = M_ker[1]

# d = a x b = (d12, -d02, d01)
# d is in ker(h), so d = lam * v1 + mu * v2 over QQ:
coords = M_ker.solve_left(vector(QQ, d))
print("coords over QQ:", coords)
print("Are coords integers?", all(x in ZZ for x in coords))
lam_val, mu_val = ZZ(coords[0]), ZZ(coords[1])
print(f"lam = {lam_val}, mu = {mu_val}")

# z1 = 2 * L^T * v1 / n
# z2 = 2 * L^T * v2 / n
z1 = vector(QQ, [QQ(2 * sum(L[j, i] * v1[j] for j in range(3))) / n for i in range(3)])
z2 = vector(QQ, [QQ(2 * sum(L[j, i] * v2[j] for j in range(3))) / n for i in range(3)])

# c x w:
def cross_prod(u, v):
    return vector(ZZ, [
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    ])

cxw = cross_prod(c, w)
target = - (lam_val * z1 + mu_val * z2)

print("cxw:", cxw)
print("target:", target)
print("cxw == target:", cxw == target)
