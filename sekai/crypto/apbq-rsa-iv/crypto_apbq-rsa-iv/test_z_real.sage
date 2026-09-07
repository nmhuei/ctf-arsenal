with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

M = Matrix(ZZ, [[h0, h1, h2], [n, 0, 0], [0, n, 0], [0, 0, n]])
L = Matrix(ZZ, [r for r in M.hermite_form().rows() if vector(r).norm() > 0]).LLL()

M_ker = Matrix(ZZ, [list(hints)]).right_kernel().basis_matrix().LLL()
v1 = M_ker[0]
v2 = M_ker[1]

Lv1 = L * v1
Lv2 = L * v2

print("Lv1 % n == 0:", [x % n == 0 for x in Lv1])
print("Lv2 % n == 0:", [x % n == 0 for x in Lv2])

z1 = vector(ZZ, [x // n for x in Lv1])
z2 = vector(ZZ, [x // n for x in Lv2])

print("z1:", z1)
print("z2:", z2)
print("z1 bit lengths:", [abs(x).bit_length() for x in z1])
print("z2 bit lengths:", [abs(x).bit_length() for x in z2])
