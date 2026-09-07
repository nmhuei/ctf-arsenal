import random
from Crypto.Util.number import getPrime

p = getPrime(60)
q = getPrime(60)
n = p * q
B = 2**18

a = [random.randint(1, B) for _ in range(3)]
b = [random.randint(1, B) for _ in range(3)]
h = [a[i]*p + b[i]*q for i in range(3)]

# D = q*b - p*a:
D = [b[i]*q - a[i]*p for i in range(3)]

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
D_vec = vector(ZZ, D)

c = L.solve_left(H_vec)
print("c:", c)
print("c in ZZ?", [x in ZZ for x in c])

u = L.solve_left(D_vec)
print("u:", u)
print("u in ZZ?", [x in ZZ for x in u])
