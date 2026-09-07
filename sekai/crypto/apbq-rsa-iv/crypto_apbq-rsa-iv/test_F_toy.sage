import random
from Crypto.Util.number import getPrime

p = getPrime(60)
q = getPrime(60)
n = p * q
B = 2**18

a = [random.randint(1, B) for _ in range(3)]
b = [random.randint(1, B) for _ in range(3)]
h = [a[i]*p + b[i]*q for i in range(3)]

M = Matrix(ZZ, [
    [h[0], h[1], h[2]],
    [n,    0,    0   ],
    [0,    n,    0   ],
    [0,    0,    n   ]
])
HNF = M.hermite_form()
HNF_rows = [r for r in HNF.rows() if vector(r).norm() > 0]
L = Matrix(ZZ, HNF_rows).LLL()

H_vec = vector(ZZ, h)
pa = vector(ZZ, [a[i]*p for i in range(3)])

c_pa = [ZZ(x) for x in L.solve_left(pa)]
x_true = c_pa[0]
y_true = c_pa[1]

print("x_true:", x_true)
print("y_true:", y_true)

for j in range(3):
    u_j = x_true * L[0][j] + y_true * L[1][j]
    v_j = H_vec[j] - u_j
    val = (u_j * v_j) % n
    print(f"j={j}: (u_j * v_j) % n == 0:", val == 0)
    print(f"j={j}: gcd(u_j, n) == p:", gcd(u_j, n) == p, "gcd(u_j, n) == q:", gcd(u_j, n) == q)
