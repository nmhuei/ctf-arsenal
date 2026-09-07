load('test_clean_50_toy.sage')

# We have 3 base polynomials: E0, E1, E2:
E0 = E[0]
E1 = E[1]
E2 = E[2]

# Let's collect shift polynomials from E0, E1, E2:
shift_polys = []

# Degree 6 (mod n^3):
# From E0:
shift_polys.append(E0^3)
# From E1:
shift_polys.append(E1^3)
# From E2:
shift_polys.append(E2^3)
# Mixed:
shift_polys.append(E0^2 * E1)
shift_polys.append(E0^2 * E2)
shift_polys.append(E0 * E1^2)
shift_polys.append(E0 * E2^2)
shift_polys.append(E1^2 * E2)
shift_polys.append(E1 * E2^2)
shift_polys.append(E0 * E1 * E2)

# Degree 4 * n (mod n^3):
shift_polys.append(n * E0^2)
shift_polys.append(n * E1^2)
shift_polys.append(n * E2^2)
shift_polys.append(n * E0 * E1)
shift_polys.append(n * E0 * E2)
shift_polys.append(n * E1 * E2)

# Monomial shifts:
# n * m2 * E0^2, n * m2 * E1^2, n * m2 * E2^2 (only as needed)
for m in deg_monos[2]:
    shift_polys.append(n * m * E0^2)
    shift_polys.append(n * m * E1^2)
    shift_polys.append(n * m * E2^2)

# Degree 2 * n^2 (mod n^3):
shift_polys.append(n^2 * E0)
shift_polys.append(n^2 * E1)
shift_polys.append(n^2 * E2)

for m in deg_monos[2]:
    shift_polys.append(n^2 * m * E0)
    shift_polys.append(n^2 * m * E1)
    shift_polys.append(n^2 * m * E2)

for m in deg_monos[4]:
    shift_polys.append(n^2 * m * E0)

print(f"Total candidate shift polynomials: {len(shift_polys)}")

# Find pivots over QQ:
M_shift = Matrix(QQ, len(shift_polys), n_monos)
for r_idx, poly in enumerate(shift_polys):
    for c_idx, m in enumerate(monos):
        M_shift[r_idx, c_idx] = poly.monomial_coefficient(m)

pivots = M_shift.pivots()
print(f"Pivots of shift polynomials: {len(pivots)} / {n_monos}")
non_pivots = [c for c in range(n_monos) if c not in pivots]
print(f"Non-pivot columns needed: {len(non_pivots)}")

# Exact basis: take pivot rows of M_shift:
# To preserve integer lattice, take the corresponding shift_polys:
selected_shift_polys = [shift_polys[r] for r in M_shift.pivot_rows()]
final_polys = selected_shift_polys + [(n^3) * monos[c] for c in non_pivots]

print(f"Final polynomials count: {len(final_polys)}")

M_hg = Matrix(ZZ, len(final_polys), n_monos)
for r_idx, poly in enumerate(final_polys):
    for c_idx, m in enumerate(monos):
        M_hg[r_idx, c_idx] = poly.monomial_coefficient(m) * col_weights[c_idx]

print(f"M_hg dimensions: {M_hg.dimensions()}, rank: {M_hg.rank()}")
t0 = time.time()
L_hg = M_hg.LLL()
print(f"LLL completed in {time.time() - t0:.3f}s!")

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
    for k in [2, 3, 5, 8, 12]:
        if k > len(found): break
        I = ideal([R_qq(poly) for nb, poly in found[:k]])
        print(f"Top {k} polys: ideal dim = {I.dimension()}")
        if I.dimension() == 0:
            V = I.variety()
            print("Variety:", V)
            for pt in V:
                w_cand = vector(ZZ, [round(pt[w0]), round(pt[w1]), round(pt[w2])])
                if w_cand == w or w_cand == -w:
                    print(f"[!] SUCCESS! RECOVERED w = {w_cand}!")
            break
