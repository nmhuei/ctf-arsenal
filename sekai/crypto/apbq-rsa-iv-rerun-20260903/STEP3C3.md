# Micro-step 3C3

Scope: local dimension-reduction analysis only. Read only STEP3C2.md, RELATION_RESULTS.json, lattice_relations.py, lifted_constraints.py, STEP3B.md, and STEP3C1.md. No original source, INSTANCE.json, ciphertext/plaintext handling, network access, external directories, writeup search, solution repository, or pre-existing answer was used.

## Implemented

Created reduced_search.py.

The previous step established that direct enumeration of the bounded (lambda, mu) rectangle has an 851-bit candidate count and is infeasible. This step therefore tested the smallest exact dimension reduction available from the recorded relations.

For each fixed hint index i, STEP3C1 records two ordered-pair equations whose modular residue is the same hidden small value A_i. Writing d_ij^2 as its lifted linear form in x=(u,v,w), eliminating A_i gives the candidate homogeneous congruence

h_k^2 d_ij^2 - h_j^2 d_ik^2 == 0 (mod h_i).

This would reduce the problem to a three-dimensional modular-kernel lattice if any of the three resulting rows were nonzero.

reduced_search.py reconstructs these rows only from the reduced relation basis and primitive hint vector already recorded in STEP3B.md. It also includes a synthetic exact-identity test before applying the construction to the recorded public relation data.

## Bounded run

Command:

timeout 30s python3 reduced_search.py

Observed exit status: 2.

Observed output:

text
PASS synthetic cancellation identity
METHOD=eliminate_A_i_then_modular_kernel_reduction
row (0, 1, 2) modulus_bits 1647 coefficients (0, 0, 0) identically_zero True
row (1, 0, 2) modulus_bits 1649 coefficients (0, 0, 0) identically_zero True
row (2, 0, 1) modulus_bits 1648 coefficients (0, 0, 0) identically_zero True
nonzero_eliminated_rows = 0
coordinate_pair_count_bits = 851
concrete_numeric_n_assignments_in_allowed_artifacts = 0
REDUCTION_RESULT=DEGENERATE_KERNEL_NO_INSTANTIATED_ROWS
concrete_blocker = eliminating the three small A_i residues produces only identically zero congruences on the exact relation basis; the allowed artifacts record the symbolic n-dependent rows but no concrete n or instantiated residue-coefficient rows.
next_smallest_local_experiment = supply only the three instantiated independent residue coefficient rows (or equivalently the concrete public n) as a sanitized local artifact, then run a scaled 6D low-residue lattice LLL/BKZ with x=(u,v,w) scaled by 2^399 to match the 2^1248 residue bound.


## Exact outcome

The attempted 3D reduction is mathematically degenerate on the exact relation basis: all three A_i-eliminated congruences are identically zero. Therefore they impose no restriction at all on (u,v,w) and cannot reduce the 851-bit search space.

The remaining useful constraints are the six small-residue equations from STEP3C1,

L_ij(u,v,w) = -n*(h_j^2)^(-1)*d_ij^2 (mod h_i), with residue in [0, B^2].

However, among the permitted artifacts there is no concrete numeric assignment for n and no already-instantiated residue-coefficient rows. lifted_constraints.py contains only the symbolic construction that reads n from a disallowed file at runtime. Consequently a nontrivial modular-kernel, closest-vector, or low-residue lattice cannot be instantiated while obeying this step's read restriction.

This is the concrete blocker; no survivor or hidden value is claimed.

## Next smallest local experiment

With only a sanitized local artifact containing the three independent instantiated residue-coefficient rows, or equivalently the concrete public n, construct the low-residue lattice for x=(u,v,w) plus three quotient coordinates. Scale the lifted coordinates by approximately 2^399, because their bounds are about 2^849 while each residue is below about 2^1248, then run LLL followed by a small BKZ/closest-vector experiment. This is six-dimensional and is the smallest non-degenerate lattice experiment suggested by the currently recorded exact constraints.

STEP3C3_COMPLETE
