import time
from Crypto.Util.number import long_to_bytes

t0 = time.time()
print("[*] Loading challenge parameters...")
with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

# 1. Public lattice Lambda in Z^3:
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
print(f"[+] Lattice reduced! c = {c}")

ks = [(L[i][0] * pow(int(h0), -1, n)) % n for i in range(3)]

R.<w0, w1, w2> = ZZ[]

# Even monomials up to degree 4:
monos = []
deg_monos = {0: [], 2: [], 4: []}
for deg in [0, 2, 4]:
    for i in range(deg, -1, -1):
        for j in range(deg - i, -1, -1):
            k = deg - i - j
            m = w0^i * w1^j * w2^k
            monos.append(m)
            deg_monos[deg].append(m)

n_monos = len(monos)
print(f"Total monomials: {n_monos}")

raw_polys = [(ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1]
for j in range(3):
    raw_polys.append((w0*L[0, j] + w1*L[1, j] + w2*L[2, j])^2 - H[j]^2)

E = []
for P in raw_polys:
    E.append(sum(((P.monomial_coefficient(m) % n)) * m for m in deg_monos[2] + [R(1)]))

all_polys = []

# Group 1: E_i * E_j (deg 4, multiple of n^0 = 1)
for i in range(4):
    for j in range(i, 4):
        all_polys.append(E[i] * E[j])

# Group 2: n * m2 * E_k (deg 4, multiple of n^1)
for m in deg_monos[2]:
    for k in range(4):
        all_polys.append(n * m * E[k])

# Group 3: n * E_k (deg 2, multiple of n^1)
for k in range(4):
    all_polys.append(n * E[k])

# Group 4: CORRECT MODULUS SHIFTS:
# deg 4: n^(2 - 2) * m = 1 * m
# BUT WAIT: Does 1 * m vanish mod n^2 at w?
# NO! 1 * m DOES NOT vanish mod n^2 at w!
# ONLY multiples of n^2 vanish mod n^2, UNLESS the polynomial is constructed from E!
