load('solve_quad_kernel.sage')

R.<A, B> = QQ[]

# x = A * r0 + B * r1
# indices: 0: x1, 1: x2, 2: x3, 3: x4, 4: x5

x1 = A * r0[0] + B * r1[0]
x2 = A * r0[1] + B * r1[1]
x3 = A * r0[2] + B * r1[2]
x4 = A * r0[3] + B * r1[3]
x5 = A * r0[4] + B * r1[4]

eq1 = x1 * x2 - x5^2
eq2 = x3 * x5 - x1 * x4
eq3 = x4 * x5 - x2 * x3

print("eq1:", eq1)
print("eq2:", eq2)
print("eq3:", eq3)

# Since they are homogeneous in (A, B), set B = 1 and solve in A:
R_a.<a> = QQ[]
poly1 = eq1(a, 1)
poly2 = eq2(a, 1)
poly3 = eq3(a, 1)

g12 = gcd(poly1, poly2)
print("gcd(poly1, poly2):", g12)
g123 = gcd(g12, poly3)
print("gcd(poly1, poly2, poly3):", g123)

roots = g123.roots()
print("Common roots in QQ:", roots)
