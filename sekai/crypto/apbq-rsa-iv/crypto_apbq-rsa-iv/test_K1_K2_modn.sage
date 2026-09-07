with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

M = Matrix(ZZ, [[h0, h1, h2], [n, 0, 0], [0, n, 0], [0, 0, n]])
L = Matrix(ZZ, [r for r in M.hermite_form().rows() if vector(r).norm() > 0]).LLL()
H = vector(ZZ, [h0, h1, h2])
c = vector(ZZ, [ZZ(x) for x in L.solve_left(H)])
ks = vector(ZZ, [(L[i][0] * pow(int(h0), -1, n)) % n for i in range(3)])

M_ker = Matrix(ZZ, [list(hints)]).right_kernel().basis_matrix().LLL()
v1 = M_ker[0]
v2 = M_ker[1]

z1 = vector(ZZ, [x // n for x in L * v1])
z2 = vector(ZZ, [x // n for x in L * v2])

def cross_prod(u, v):
    return vector(ZZ, [
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    ])

z1xc = cross_prod(z1, c)
z2xc = cross_prod(z2, c)
c_norm_sq = c * c

inv_c_norm_sq = pow(int(c_norm_sq), -1, n)

K1 = (2 * (ks * z1xc) * inv_c_norm_sq) % n
K2 = (2 * (ks * z2xc) * inv_c_norm_sq) % n

print("K1:", K1)
print("K2:", K2)
print("K1 bit length:", K1.bit_length())
print("K2 bit length:", K2.bit_length())
