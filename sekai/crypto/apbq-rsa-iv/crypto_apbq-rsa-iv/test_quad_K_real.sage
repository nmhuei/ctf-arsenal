with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

M = Matrix(ZZ, [
    [h0, h1, h2],
    [n,  0,  0 ],
    [0,  n,  0 ],
    [0,  0,  n ]
])
HNF = M.hermite_form()
HNF_rows = [r for r in HNF.rows() if vector(r).norm() > 0]
L = Matrix(ZZ, HNF_rows).LLL()

H = vector(ZZ, [h0, h1, h2])
c = vector(ZZ, [ZZ(x) for x in L.solve_left(H)])

K01 = vector(ZZ, [ZZ((L[i, 1]*H[0] - L[i, 0]*H[1]) / n) for i in range(3)])
K02 = vector(ZZ, [ZZ((L[i, 2]*H[0] - L[i, 0]*H[2]) / n) for i in range(3)])
K12 = vector(ZZ, [ZZ((L[i, 2]*H[1] - L[i, 1]*H[2]) / n) for i in range(3)])

print("K01 norm bits:", vector(K01).norm().n().log(2))
print("K02 norm bits:", vector(K02).norm().n().log(2))
print("K12 norm bits:", vector(K12).norm().n().log(2))

# Verify c . K == 0:
print("K01 . c == 0:", K01 * c == 0)
print("K02 . c == 0:", K02 * c == 0)
print("K12 . c == 0:", K12 * c == 0)
