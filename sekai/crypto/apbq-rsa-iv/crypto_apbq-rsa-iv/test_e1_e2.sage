with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

M = Matrix(ZZ, [[h0, h1, h2], [n, 0, 0], [0, n, 0], [0, 0, n]])
L = Matrix(ZZ, [r for r in M.hermite_form().rows() if vector(r).norm() > 0]).LLL()
H = vector(ZZ, [h0, h1, h2])
c = vector(ZZ, [ZZ(x) for x in L.solve_left(H)])

M_ker = Matrix(ZZ, [list(hints)]).right_kernel().basis_matrix().LLL()
v1 = M_ker[0]
v2 = M_ker[1]

# z1 = 2 * L^T * v1 / n
# z2 = 2 * L^T * v2 / n
z1 = vector(QQ, [QQ(2 * sum(L[j, i] * v1[j] for j in range(3))) / n for i in range(3)])
z2 = vector(QQ, [QQ(2 * sum(L[j, i] * v2[j] for j in range(3))) / n for i in range(3)])

print("z1 norm bits:", vector(z1).norm().n().log(2))
print("z2 norm bits:", vector(z2).norm().n().log(2))

# c x z1 and c x z2:
c_Q = vector(QQ, c)
c_norm_sq = c_Q * c_Q

# Vector cross product in 3D:
def cross_prod(u, v):
    return vector(QQ, [
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    ])

e1 = cross_prod(c_Q, z1) / c_norm_sq
e2 = cross_prod(c_Q, z2) / c_norm_sq

print("e1 norm bits:", vector(e1).norm().n().log(2))
print("e2 norm bits:", vector(e2).norm().n().log(2))

# Check e1 . c and e2 . c:
print("e1 . c:", e1 * c_Q)
print("e2 . c:", e2 * c_Q)
