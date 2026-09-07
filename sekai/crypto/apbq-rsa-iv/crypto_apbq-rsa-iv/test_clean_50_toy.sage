import random, time
from Crypto.Util.number import getPrime, long_to_bytes

p = getPrime(60)
q = getPrime(60)
n = p * q
B = 2**18

a = vector(ZZ, [random.randint(1, B) for _ in range(3)])
b = vector(ZZ, [random.randint(1, B) for _ in range(3)])
h = a*p + b*q

M = Matrix(ZZ, [
    list(h),
    [n, 0, 0],
    [0, n, 0],
    [0, 0, n]
])
HNF = M.hermite_form()
HNF_rows = [r for r in HNF.rows() if vector(r).norm() > 0]
L = Matrix(ZZ, HNF_rows).LLL()

H = vector(ZZ, h)
pa = vector(ZZ, [a[i]*p for i in range(3)])
qb = vector(ZZ, [b[i]*q for i in range(3)])

c = vector(ZZ, [ZZ(x) for x in L.solve_left(H)])
u = vector(ZZ, [ZZ(x) for x in L.solve_left(pa)])
v = vector(ZZ, [ZZ(x) for x in L.solve_left(qb)])
w = u - v

ks = [(L[i][0] * pow(int(h[0]), -1, n)) % n for i in range(3)]

R.<w0, w1, w2> = ZZ[]

# Even monomials up to degree 6:
monos = []
deg_monos = {0: [], 2: [], 4: [], 6: []}
for deg in [0, 2, 4, 6]:
    for i in range(deg, -1, -1):
        for j in range(deg - i, -1, -1):
            k = deg - i - j
            m = w0^i * w1^j * w2^k
            monos.append(m)
            deg_monos[deg].append(m)

n_monos = len(monos)

# Single base polynomial P:
P_raw = (ks[0]*w0 + ks[1]*w1 + ks[2]*w2)^2 - 1
P = sum(((P_raw.monomial_coefficient(m) % n)) * m for m in deg_monos[2] + [R(1)])

# Let's collect all candidate shift polynomials:
shift_polys = []

# j = 3: P^3 (mod n^3)
shift_polys.append(P^3)

# j = 2: n * m2 * P^2 (deg 6) and n * P^2 (deg 4)
for m in deg_monos[2]:
    shift_polys.append(n * m * P^2)
shift_polys.append(n * P^2)

# j = 1: n^2 * m4 * P (deg 6) and n^2 * m2 * P (deg 4) and n^2 * P (deg 2)
for m in deg_monos[4]:
    shift_polys.append(n^2 * m * P)
for m in deg_monos[2]:
    shift_polys.append(n^2 * m * P)
shift_polys.append(n^2 * P)

print(f"Shift polynomials from P: {len(shift_polys)}")

# Find echelon form of shift_polys over QQ to find pivots:
M_shift = Matrix(QQ, len(shift_polys), n_monos)
for r_idx, poly in enumerate(shift_polys):
    for c_idx, m in enumerate(monos):
        M_shift[r_idx, c_idx] = poly.monomial_coefficient(m)

pivots = M_shift.pivots()
print(f"Pivots of shift polynomials: {len(pivots)} / {n_monos}")
non_pivots = [c for c in range(n_monos) if c not in pivots]
print(f"Non-pivot columns needed: {len(non_pivots)}")

# Exactly len(pivots) + len(non_pivots) = 50 polynomials!
# Build exact 50x50 lattice:
final_polys = list(shift_polys)
for col_idx in non_pivots:
    final_polys.append((n^3) * monos[col_idx])

print(f"Final polynomials count: {len(final_polys)}")

W0 = 1 << (abs(w[0]).bit_length() + 2)
W1 = 1 << (abs(w[1]).bit_length() + 2)
W2 = 1 << (abs(w[2]).bit_length() + 2)

col_weights = []
for m in monos:
    exp = m.exponents()[0]
    col_weights.append(W0^exp[0] * W1^exp[1] * W2^exp[2])

M_hg = Matrix(ZZ, len(final_polys), n_monos)
for r_idx, poly in enumerate(final_polys):
    for c_idx, m in enumerate(monos):
        M_hg[r_idx, c_idx] = poly.monomial_coefficient(m) * col_weights[c_idx]

print(f"M_hg dimensions: {M_hg.dimensions()}, rank: {M_hg.rank()}")
t0 = time.time()
L_hg = M_hg.LLL()
print(f"LLL on {M_hg.nrows()}x{M_hg.ncols()} completed in {time.time() - t0:.3f}s!")

target_norm_bits = (n^3).bit_length()
print(f"Target norm bits (n^3): {target_norm_bits}")

found = []
for idx, r in enumerate(L_hg.rows()):
    if vector(r).norm() == 0: continue
    norm = vector(r).norm().n()
    if norm.log(2) < target_norm_bits:
        poly = sum((r[c_idx] // col_weights[c_idx]) * monos[c_idx] for c_idx in range(n_monos))
        if not poly.is_constant():
            found.append((norm.log(2), poly))

print(f"[+] Found {len(found)} polynomials with norm < n^3!")
for idx, (nb, poly) in enumerate(found[:5]):
    print(f"  Poly {idx}: norm bits = {nb:.1f}, poly(w) == 0: {poly(w[0], w[1], w[2]) == 0}")

if found:
    R_qq.<w0, w1, w2> = QQ[]
    for k in [3, 5, 10]:
        I = ideal([R_qq(poly) for nb, poly in found[:k]])
        print(f"Top {k} polys: ideal dim = {I.dimension()}")
        if I.dimension() == 0:
            V = I.variety()
            print("Variety:", V)
            break
