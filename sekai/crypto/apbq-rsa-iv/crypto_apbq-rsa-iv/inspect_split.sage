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

H = vector(ZZ, h)
pa = vector(ZZ, [a[i]*p for i in range(3)])
qb = vector(ZZ, [b[i]*q for i in range(3)])

c = vector(ZZ, [ZZ(x) for x in L.solve_left(H)])
c_pa = L.solve_left(pa)
c_qb = L.solve_left(qb)

print("c:", c)
print("c_pa:", c_pa)
print("c_qb:", c_qb)
print("Are c_pa integers?", [x in ZZ for x in c_pa])
print("Are c_qb integers?", [x in ZZ for x in c_qb])
