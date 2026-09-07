with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

M = Matrix(ZZ, [[h0, h1, h2], [n, 0, 0], [0, n, 0], [0, 0, n]])
L = Matrix(ZZ, [r for r in M.hermite_form().rows() if vector(r).norm() > 0]).LLL()

M_ker = Matrix(ZZ, [list(hints)]).right_kernel().basis_matrix().LLL()
v1 = M_ker[0]
v2 = M_ker[1]

# w1 = (L^T * v1) mod n
# w2 = (L^T * v2) mod n
w1 = vector(ZZ, [(sum(L[j, i] * v1[j] for j in range(3))) % n for i in range(3)])
w2 = vector(ZZ, [(sum(L[j, i] * v2[j] for j in range(3))) % n for i in range(3)])

print("w1 mod n:", [x.bit_length() for x in w1])
print("w2 mod n:", [x.bit_length() for x in w2])

# Ratio - w2[0] / w1[0] mod n:
ratio0 = (- w2[0] * pow(int(w1[0]), -1, n)) % n
ratio1 = (- w2[1] * pow(int(w1[1]), -1, n)) % n
ratio2 = (- w2[2] * pow(int(w1[2]), -1, n)) % n

print("ratio0 == ratio1:", ratio0 == ratio1)
print("ratio1 == ratio2:", ratio1 == ratio2)
print("ratio0 bit length:", ratio0.bit_length())
