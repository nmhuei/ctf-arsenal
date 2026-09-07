load('test_5d_synthetic.sage')

# In synthetic:
M = Matrix(ZZ, [[h[0], h[1], h[2]], [n, 0, 0], [0, n, 0], [0, 0, n]])
L = Matrix(ZZ, [r for r in M.hermite_form().rows() if vector(r).norm() > 0]).LLL()

print("det(L) == n^2:", L.det() == n^2)
Fp = GF(p)
L_p = Matrix(Fp, L)
print("rank of L mod p:", L_p.rank())

Fq = GF(q)
L_q = Matrix(Fq, L)
print("rank of L mod q:", L_q.rank())
