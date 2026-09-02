#!/usr/bin/env sage
"""
SekaiCTF 2026 - Needle in a Multivariate Sekai
Lattice-based GPV-style signature forgery attack

Attack: Given 200 message-signature pairs, forge a signature for "STAGE OF SEKAI"
by solving the quadratic form equation v^T * M_pk * v = t_target.
"""

import sys, os, json, ast
from hashlib import sha256 as py_sha256
from sage.all import *

# ============================================================
# Load data
# ============================================================
base = sys.argv[1] if len(sys.argv) > 1 else "chal"

pk_data = load(os.path.join(base, "pk.sobj"))
params = pk_data['params']
pk = pk_data['pk']

print("Params:", params['m'], params['B1'], params['B0'])
print("PK dims:", pk.dimensions())
print("PK symmetric:", pk == pk.transpose())
print("PK det bits:", pk.det().nbits())

m = params['m']
B1 = params['B1']
B0 = params['B0']
k = Integer(8)
n = m + 2*k

print(f"m={m}, k={k}, n={n}")

# Load sigs
with open(os.path.join(base, "output.txt"), "r") as f:
    sigs_str = f.read()
sig_lists = ast.literal_eval(sigs_str)
sig_vecs = [vector(ZZ, s) for s in sig_lists]
K = len(sig_vecs)
print(f"Signatures: {K}, dim: {len(sig_vecs[0])}")

# Target t
t_target = Integer(int.from_bytes(b"\x01" + py_sha256(b"STAGE OF SEKAI").digest(), 'big'))
print(f"t_target bits: {t_target.nbits()}")

# Known t values
t_vals = []
for i in range(K):
    msg = "message %d" % i
    t = Integer(int.from_bytes(b"\x01" + py_sha256(msg.encode()).digest(), 'big'))
    t_vals.append(t)

print("t bits:", [t.nbits() for t in t_vals[:5]])
print("t_target:", t_target)
print("t_target bits:", t_target.nbits())

# ============================================================
# Verify
# ============================================================
print("\n--- Verification ---")
for i in range(min(3, K)):
    r = sig_vecs[i] * pk * sig_vecs[i]
    ok = (r == t_vals[i])
    print(f"  Sig {i}: {ok}")

# ============================================================
# Cholesky & y-vectors
# ============================================================
print("\n--- Cholesky decomposition ---")
R = pk.cholesky()
print("R dims:", R.dimensions())

y_vecs = [R * v for v in sig_vecs]

# ============================================================
# Gram matrix (first K sigs)
# ============================================================
print("\n--- Gram matrix ---")

# Only compute up to 50 to save time
k_gram = min(50, K)
print("Computing %dx%d Gram..." % (k_gram, k_gram))
t0 = walltime()
Gram = matrix(ZZ, k_gram, k_gram)
for i in range(k_gram):
    for j in range(k_gram):
        Gram[i,j] = y_vecs[i] * y_vecs[j]
t1 = walltime()
print("  took %.1fs" % (t1 - t0))

off_max = max(abs(Gram[i,j]) for i in range(k_gram) for j in range(k_gram) if i != j)
diag_vals = [Gram[i,i] for i in range(k_gram)]
print("Off-diag max:", off_max)
print("Diag min:", min(diag_vals))
print("Diag max:", max(diag_vals))

# Check orthogonal structure
diag_Gram = diagonal_matrix(diag_vals)
diff = Gram - diag_Gram
print("Frob off-diag:", diff.norm('frob').n())
print("Rel Frob:", (diff.norm('frob') / Gram.norm('frob')).n())

# ============================================================
# Approach 1: Try small integer combinations
# ============================================================
print("\n=== Approach 1: Small integer combinations ===")

# For each pair (i,j) with i != j, check if a^2*t_i + b^2*t_j + 2ab*G[i,j] = t_target
# for small a,b
print("Checking pairwise...")
found = False
for i in range(min(10, K)):
    for j in range(i+1, min(10, K)):
        Gij = Gram[i,j] if i < k_gram and j < k_gram else (y_vecs[i] * y_vecs[j])
        for a in range(-3, 4):
            for b in range(-3, 4):
                if a == 0 and b == 0:
                    continue
                val = a*a*t_vals[i] + b*b*t_vals[j] + 2*a*b*Gij
                if val == t_target:
                    sig_f = a*sig_vecs[i] + b*sig_vecs[j]
                    check = sig_f * pk * sig_f
                    print("  FOUND! a=%d, b=%d, i=%d, j=%d, check=%d" % (a, b, i, j, check))
                    found = True

if not found:
    print("  Nothing in small search (a,b in {-3..3}, 10 sigs)")

# ============================================================
# Approach 2: LLL on Gram matrix
# ============================================================
print("\n=== Approach 2: LLL Gram decomposition ===")

# We want c^T * Gram * c = t_target with c in Z^K
# If G = L^T * L (Cholesky), we need ||L*c||^2 = t_target
# The lattice L_Gram = {L*c : c in Z^K} has K basis vectors

# Build the lattice basis from Gram Cholesky
# Since Gram may be singular, use full Gram

try:
    G_chol = Gram.cholesky()
    print("Gram Cholesky done, shape:", G_chol.dimensions())

    # LLL the Gram Cholesky basis
    print("LLL on Gram Cholesky...")
    G_lll = G_chol.LLL()
    print("  done")

    # Check if we can find a short vector with norm^2 = t_target
    norms = [(G_lll[i]*G_lll[i], i) for i in range(k_gram)]
    norms_sorted = sorted([(n, i) for n, i in norms])
    print("  Smallest norms squared:", [n for n, i in norms_sorted[:10]])

    # Try to find combination of LLL-reduced basis vectors with norm^2 = t_target
    # Since we can scale LLL vectors arbitrarily, we look at the lattice {sum(c_i * LLL_i)}
    # Each LLL_i has small Gram norm

    # We want v = sum(c_i * LLL_i) with ||v||^2 = t_target
    # If LLL_i are close to orthogonal with norms l_i^2, we need sum(c_i^2 * l_i^2) + cross = t_target

    # Try combinations of LLL vectors
    def find_lattice_combination(LLL_basis, target_sq, max_coeff=2, depth=0, max_depth=5):
        if depth > max_depth:
            return None
        if len(LLL_basis) == 0:
            return None

        # Try just this vector scaled
        v0 = LLL_basis[0]
        n0 = v0 * v0
        if n0 > 0:
            for c in range(-max_coeff, max_coeff+1):
                if c == 0:
                    continue
                val = c*c*n0
                if val == target_sq:
                    return {0: c}

        # Try adding combinations from rest
        rest = LLL_basis[1:]
        sub = find_lattice_combination(rest, target_sq, max_coeff, depth+1, max_depth)
        if sub is not None:
            return {k+1: v for k, v in sub.items()}

        for c in range(-max_coeff, max_coeff+1):
            if c == 0:
                continue
            val = c*c*n0
            if val > target_sq:
                continue
            sub = find_lattice_combination(rest, target_sq - val, max_coeff, depth+1, max_depth)
            if sub is not None:
                result = {0: c}
                result.update({k+1: v for k, v in sub.items()})
                return result
        return None

    comb = find_lattice_combination(G_lll, t_target, max_coeff=3, max_depth=6)
    if comb is not None:
        print("  Found combination:", comb)
except Exception as e:
    print("  Error:", e)
    import traceback
    traceback.print_exc()

# ============================================================
# Approach 3: Embedding in CVP lattice
# ============================================================
print("\n=== Approach 3: CVP with the lattice of y-vectors ===")

# The y_i = R * sig_i are lattice points in L_R = R * Z^n
# We need to find y in L_R with ||y||^2 = t_target

# Build lattice from y_i (they span a sublattice)
# Actually, any y in L_R is valid since sig = R^-1 * y is integer iff y in L_R

# Let's use the standard basis of L_R
# L_R has basis {R * e_1, ..., R * e_n}
B_std = matrix(QQ, n, n)
for i in range(n):
    B_std[i] = R * vector(ZZ, [1 if j==i else 0 for j in range(n)])

print("Standard basis det:", abs(B_std.det()).n())
print("Expected det:", sqrt(abs(pk.det())).n())

# LLL reduce
print("LLL...")
B_lll = B_std.LLL()
print("  done")

# Verify smallest vector
v0 = B_lll[0]
print("Smallest norm^2 in LLL basis:", (v0*v0).n())

# Approach: Use Babai to find lattice point close to a random point on sphere
# Let target = random point on sphere of radius sqrt(t_target), then find
# nearest lattice point
print("\nBabai nearest plane...")
target = vector(QQ, [randint(-100, 100) for _ in range(n)])
target = target / sqrt(target*target) * sqrt(QQ(t_target))

# Gram-Schmidt
G_gs, mu = B_lll.gram_schmidt()

# Babai nearest plane
babai = vector(QQ, n)
t = target
for i in reversed(range(n)):
    ti = t * G_gs[i] / (G_gs[i] * G_gs[i])
    ci = round(ti)
    babai += ci * B_lll[i]
    t -= ci * G_gs[i]

diff = babai - target
norm_sq = babai * babai
print("Babai result norm^2:", norm_sq.n())
print("Target norm^2:", t_target)
print("Diff:", (norm_sq - t_target).n())

# Try iterating nearby lattice vectors
print("\nSearching neighbors...")
best_diff = abs(norm_sq - t_target)
best_vec = babai
# Check if babai is integer and verify
sig_test = vector(ZZ, [round(x) for x in (R.inverse() * babai)])
try:
    check = sig_test * pk * sig_test
    print("  Babai sig check:", check == t_target)
except:
    pass

# Search in a small box
for delta in [(1,0,0), (0,1,0), (0,0,1), (-1,0,0), (0,-1,0), (0,0,-1)]:
    for i in range(n):
        for sign in [1, -1]:
            v = babai + sign * B_lll[i]
            nsq = v * v
            diff = abs(nsq - t_target)
            if diff < best_diff:
                best_diff = diff
                best_vec = v
                if nsq == t_target:
                    print("  FOUND exact norm with LLL basis %d + sign %d" % (i, sign))

print("Best diff:", best_diff.n())
print("Best norm^2:", (best_vec*best_vec).n())

# ============================================================
# Approach 4: Use Gram matrix lattice reduction in coefficient space
# ============================================================
print("\n=== Approach 4: Gram SVP via LLL ===")

# We want to find c in Z^K such that c^T * G * c = t_target
# Let's build the lattice:
# [L    0]
# [c^T  t_target]  where L*L^T = G (Cholesky)
# Actually, better: use Korkin-Zolotarev or embedding

# Since the main issue is finding integer c with the right Gram norm,
# build lattice from Gram rows and search

# Let's compute full Gram for all 200 sigs
print("Computing full Gram matrix...")
t0 = walltime()
Gram_full = matrix(ZZ, K, K)
for i in range(K):
    for j in range(i, K):
        g = y_vecs[i] * y_vecs[j]
        Gram_full[i,j] = g
        Gram_full[j,i] = g
print("  took %.1fs" % (walltime() - t0))

# Rank analysis
eigs = Gram_full.eigenvalues()
print("Gram rank:", sum(1 for e in eigs if abs(e) > 1e-10))
print("Full Gram off-diag max:", max(abs(Gram_full[i,j]) for i in range(K) for j in range(K) if i != j))

# ============================================================
# Approach 5: Solve using Babai on sig lattice
# ============================================================
print("\n=== Approach 5: Find v = sum(c_i * sig_i) via lattice CVP ===")

# Build a K×K lattice from pure Gram matrix
# Gram = S * pk * S^T = Y * Y^T where Y = [y_0, ..., y_{K-1}] is n×K

# Let Y_mat = matrix(QQ, n, K) with columns y_i
Y_mat = matrix(QQ, n, K)
for i in range(K):
    Y_mat.set_column(i, y_vecs[i])

# Gram = Y_mat^T * Y_mat (K×K)
# We want c such that ||Y_mat * c||^2 = t_target

# Find Q, R where Y_mat = Q * R (QR decomposition)
print("QR decomposition of Y_mat...")
Q, R_mat = Y_mat.QR()
print("  Q:", Q.dimensions(), "R:", R_mat.dimensions())

# Now ||Y_mat * c||^2 = ||R_mat * c||^2 (since Q is orthogonal)
# R_mat is n×K upper triangular
# We need ||R_mat * c||^2 = t_target

# Let z = R_mat * c (z is n-dimensional)
# Then ||z||^2 = t_target and R_mat * c = z
# Since R_mat is rank r = min(n, rank(Gram)), we solve for c

# Full QR rank
r = R_mat.rank()
print("  R rank:", r)

# The first r rows of R_mat give us constraints
# c must satisfy: R_mat[:r] * c = z[:r] for some z with ||z||^2 = t_target

# Free variables in c: K - r
# We can choose random integer c, compute z = R_mat * c, and check norm

# Try random c vectors
print("\nTrying random c vectors...")
sr = matrix(ZZ, K, 1)  # We actually just need single c vectors
for attempt in range(1000):
    c_rand = vector(ZZ, [randint(-1, 1) for _ in range(K)])
    if all(ci == 0 for ci in c_rand):
        continue
    z = matrix(QQ, R_mat) * c_rand  # or simpler: sum(c_i * y_i)
    # Actually just compute directly
    y_tot = sum(c_rand[i] * y_vecs[i] for i in range(K))
    nsq = y_tot * y_tot
    if nsq == t_target:
        print("  FOUND! c:", c_rand)
        sig_f = sum(c_rand[i] * sig_vecs[i] for i in range(K))
        print("  Verified:", sig_f * pk * sig_f == t_target)
        break

    if attempt < 5:
        print("  Attempt %d: ||sum(c_i * y_i)||^2 = %d" % (attempt, nsq))

# ============================================================
# Approach 6: Direct LLL on combined space
# ============================================================
print("\n=== Approach 6: LLL on combined Gram lattice ===")

# LLL-reduce the Gram matrix directly to find short integer combinations
# We build: [I_K, 0; G, 1] and look for short rows

# Actually, let's use the Gram matrix as a lattice basis directly
# For the lattice generated by rows of Gram_full, find a vector with norm t_target

# Or simpler: use LLL on the rows of the full R * sig matrix
# to find a reduced basis, then search

# Build S_matrix: K rows of sig_vecs
S_mat = matrix(ZZ, K, n)
for i in range(K):
    for j in range(n):
        S_mat[i,j] = sig_vecs[i][j]

# LLL on S matrix (finding short combinations of sig vectors)
print("LLL on sig matrix...")
S_lll = S_mat.LLL()
print("  done")

# Check norms in pk metric
for i in range(min(20, K)):
    v = S_lll[i]
    nsq = v * pk * v
    print("  LLL row %d: pk-norm^2 = %d" % (i, nsq))
    if nsq == t_target:
        print("    *** MATCHES t_target! ***")

# ============================================================
# Approach 7: Use nearest plane on the y-space
# ============================================================
print("\n=== Approach 7: Systematic CVP on y-lattice ===")

# The lattice L_R has basis {R*e_i}. For any y in L_R,
# v = R^(-1) * y is integer.
# We need y with ||y||^2 = t_target.

# Since the signatures y_i are lattice points, let's try:
# y = a * y_i + b * LLL_row for some LLL-reduced short vector

# Get one short vector from LLL of standard basis
B_nice = B_lll[:20]  # Take 20 shortest vectors

# For each sig, try y = y_i + B_nice[j]
# Then ||y||^2 = t_i + ||B_nice[j]||^2 + 2*y_i*B_nice[j]
# We want this to equal t_target

print("Searching for close y_i + basis vector...")
for i in range(min(50, K)):
    yi = y_vecs[i]
    for j in range(len(B_nice)):
        bj = B_nice[j]
        nsq = yi*bj
        val = t_vals[i] + bj*bj + 2*nsq
        if val == t_target:
            y_f = yi + bj
            sig_f = R.inverse() * y_f
            # Check if integer
            sig_f_int = vector(ZZ, [round(x) for x in sig_f])
            check = sig_f_int * pk * sig_f_int
            print("  FOUND! i=%d, j=%d, check=%d, target=%d, match=%s" %
                  (i, j, check, t_target, check == t_target))
            if check == t_target:
                # Save solution
                with open('solution.txt', 'w') as f:
                    f.write(' '.join(str(x) for x in sig_f_int))
                print("  Solution saved!")

# ============================================================
# Approach 8: Try Cholesky factor CVP
# ============================================================
print("\n=== Approach 8: Signature as lattice + CVP ===")

# The lattice is: L = {v in Z^n : v * pk * v = t for some t}
# Actually incorrect - L = Z^n (whole space)
# The constraint is: v^T * pk * v = t_target

# But any v in Z^n has some pk-norm. We need a specific one.
# Approach: pick a vector v_0, compute its pk-norm, then
# find a short vector delta with:
#   (v_0 + delta)^T * pk * (v_0 + delta) = t_target
#   = v_0^T * pk * v_0 + 2*v_0^T * pk * delta + delta^T * pk * delta

# For a given v_0 (e.g., one of the signatures), we want delta such that
# 2*v_0^T*pk*delta + delta^T*pk*delta = t_target - t_0

# For small delta, the quadratic term is small, so
# delta^T * pk * v_0 ≈ (t_target - t_0) / 2

# This is a linear constraint! We can solve this.

# Let d = R * delta (whitened), then:
# d^T * (R^(-T) * v_0) ≈ (t_target - t_0) / 2
# = d^T * y_0 ≈ (t_target - t_0) / 2

# So we need d in the lattice L_R such that d dot y_0 ≈ constant.
# This is a bounded distance decoding problem.

# Since we have many y_i, we can use them as the "delta" space.

# Let's take a signature with t_i close to t_target and try to adjust
closest_i = min(range(K), key=lambda i: abs(t_vals[i] - t_target))
print("Closest sig index:", closest_i, "diff:", t_vals[closest_i] - t_target)

# We want to find delta = sum(c_j * sig_j) such that
# 2 * y_0 * (sum(c_j * y_j)) + ||sum(c_j * y_j)||^2 = target_diff

# where y_0 = R * sig_closest_i and target_diff = t_target - t_vals[closest_i]
# This is: 2 * sum(c_j * y_0^T * y_j) + sum(c_j^2 * t_j) + 2*sum(c_i*c_j*y_i*y_j) = target_diff

# For small c_j (only ±1), and if y_i are near-orthogonal:
# y_0^T*y_j ≈ 0 and y_i^T*y_j ≈ 0 for i≠j
# So: sum(c_j^2 * t_j) ≈ target_diff

# So we need c_j ∈ {-1, 0, 1} such that sum(c_j^2 * t_j) = target_diff

target_diff = t_target - t_vals[closest_i]
print("Target diff from closest sig:", target_diff)

# Find subset of t_j that sum to |target_diff|
# This is a subset sum problem. With 200 values of ~2^257, very unlikely.
# But if target_diff is small...

if abs(target_diff) < 10:
    print("Target diff is small!")
    # Try y_0 + sign * y_j for small j
    for j in range(min(20, K)):
        if j == closest_i:
            continue
        for sign in [1, -1]:
            y_f = y_vecs[closest_i] + sign * y_vecs[j]
            nsq = y_f * y_f
            if nsq == t_target:
                print("  FOUND! adjustment sig %d, sign %d" % (j, sign))
                sig_f = R.inverse() * y_f
                sig_f_int = vector(ZZ, [round(x) for x in sig_f])
                print("  Verified:", sig_f_int * pk * sig_f_int == t_target)

print("\n=== Analysis complete ===")

# Save results
results = {
    'n': int(n),
    'K': int(K),
    't_target': int(t_target),
    't_vals': [int(t) for t in t_vals],
    'pk_det_bits': int(pk.det().nbits()),
    'off_diag_max': float(off_max),
    'closest_sig_idx': int(closest_i),
    'target_diff': int(target_diff),
}
import json
with open(os.path.join(base, 'analysis_results.json'), 'w') as f:
    json.dump(results, f, indent=2, default=str)
print("Results saved!")
