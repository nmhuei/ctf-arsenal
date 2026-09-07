# Lessons Learned

## 1. Classify the primitive before choosing an attack

The exercise is not just “RSA with extra values.” The generator creates two fresh 1024-bit primes `p,q`, the modulus `n = p*q`, exponent `e = 65537`, and three hints

`h_i = a_i*p + b_i*q`

with independent bounded coefficients `0 <= a_i,b_i <= B`, where `B = 4**312 = 2**624`.

That shared bounded linear structure is the useful primitive. The ciphertext path is independent until the factors are known, so ciphertext handling should be postponed. Treat the problem first as recovery from bounded integer linear forms in the same hidden basis `(p,q)`.

## 2. Inventory every function, variable, input, and output

Before deriving anything, record the executable behavior exactly.

- `p,q`: fresh 1024-bit primes from `getPrime`.
- `n = p*q`.
- `e = 0x10001 = 65537`.
- Exactly three hint rows are generated.
- Each row samples fresh `a,b` with inclusive `randint(0, 4**312)`.
- `FLAG` is read from local `flag.txt` in binary mode and stripped.
- `m = bytes_to_long(FLAG)`.
- `c = pow(m,e,n)`.
- Output is only `n`, `c`, and `hints`.
- The fixed public instance in the source is an inert triple-quoted string during normal execution.
- The inspected source contains no network input, sockets, HTTP, stdin parser, CLI parser, or environment-variable input.

The executable is top-level code rather than a user-defined function pipeline, so the inventory must include imported operations and every top-level assignment.

## 3. Map the data flow before manipulating equations

Keep the independent paths separate:

`random primes -> p,q -> n`

`random bounded coefficients + p,q -> h_0,h_1,h_2`

`flag bytes -> strip -> bytes_to_long -> m -> RSA exponentiation -> c`

`n,c,hints -> printed public instance`

This separation prevents ciphertext logic from contaminating structural analysis of the hints.

## 4. Extract exact invariants first

For coefficient rows define

`d_ij = a_i*b_j - a_j*b_i`.

Because all coefficients lie in `[0,B]`,

`|d_ij| <= B**2 = 2**1248`.

With

`d = (d_12, -d_02, d_01)`,
`a = (a_0,a_1,a_2)`,
`b = (b_0,b_1,b_2)`,
`h = (h_0,h_1,h_2)`,

we have `d = a x b` and `h = p*a + q*b`, so the exact integer invariant is

`d . h = 0`.

This is an equality over the integers, not merely a congruence. Prefer exact equalities whenever available.

## 5. Reduce dimension before searching

Build the full integer kernel

`L = {x in Z^3 : x . h = 0}`.

It has rank two. For a primitive full basis `r,s`, write the hidden determinant vector uniquely as

`d = lambda*r + mu*s`.

The basis must be verified as the full kernel, not merely as two vectors with zero dot product. In this exercise, Step 3B verified:

- `gcd(h_0,h_1,h_2) = 1`;
- exact zero dot products;
- primitive cross-product/full-kernel behavior;
- unimodularity;
- Gauss reduction;
- nonzero minors;
- coordinate bounds;
- lifting checks.

Use actual nonzero minors and Cramer’s rule to obtain rigorous bounds on `lambda,mu`; do not rely on heuristic bit-size estimates. For the supplied instance, the final coordinate-bound bit lengths were 425 bits for `lambda` and 424 bits for `mu`.

## 6. Lift only when it linearizes useful expressions

Define

`u = lambda**2`,
`v = lambda*mu`,
`w = mu**2`.

Then preserve the exact rank-one invariant

`u*w = v**2`.

Every determinant square becomes linear:

`d_ij**2 = R_ij**2*u + 2*R_ij*S_ij*v + S_ij**2*w`

when `d_ij = R_ij*lambda + S_ij*mu`.

The concrete public bounds from Step 3C1 were:

- `lambda`: 425 bits;
- `mu`: 424 bits;
- `u`: 849 bits;
- `|v|`: 849 bits;
- `w`: 848 bits;
- `B**2`: 1249 bits.

The lift increases the principal unknown count from two to three, but it converts all determinant squares into linear forms while retaining a strong nonlinear filter.

## 7. Derive all modular relations and preserve their meaning

For each ordered pair `i != j`, the determinant identities imply

`n*d_ij**2 + A_i*h_j**2 == 0 (mod h_i)`

where

`A_i = a_i*b_i`.

If `gcd(h_i,h_j) = 1`, invert `h_j**2` modulo `h_i`:

`A_i == -n*(h_j**2)^(-1)*d_ij**2 (mod h_i)`.

Substituting the lifted form gives six modular linear rows in `(u,v,w)`, ordered as

`(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)`.

The six residues are not independent. They are exactly

`A_0,A_0,A_1,A_1,A_2,A_2`

with

`0 <= A_i <= B**2`.

The duplicate equations for each `i` are valuable consistency checks. Their differences give zero-residue congruences, but those homogeneous equations alone do not fix scale; the individual small-residue bounds do.

If a modular inverse does not exist, do not force the inverted form. Keep the non-inverted exact congruence and inspect the gcd for a simpler degeneracy.

## 8. Split independent parts into micro-steps

The files demonstrate a useful decomposition:

1. Parse the fixed local public instance.
2. Validate format, sizes, and exact source-value correspondence.
3. Build and verify the rank-two integer kernel.
4. Reduce the basis and derive rigorous coordinate bounds.
5. Construct lifted variables and six modular rows.
6. Validate the lifted algebra on synthetic data.
7. Exercise public-structure checks without assuming hidden values.
8. Only then perform candidate enumeration.
9. Reverse surviving candidates to exact determinant and `A_i` values.
10. Recover factors from an exact reversible identity.
11. Reconstruct all original hint coefficients.
12. Verify every generator equation.
13. Touch the ciphertext only after factorization is independently confirmed.

Step 3A validated only parsing/source correspondence. Step 3B validated only integer-relation machinery. Step 3C1 validated only lifted constraints and modular-row construction. This isolation makes failures attributable to one transformation.

## 9. Estimate complexity before implementation

Reject blind search over the original six 624-bit coefficients.

After reduction:

- the public kernel has rank two;
- the determinant is controlled by two bounded coordinates;
- lifting gives only three principal unknowns;
- there are six modular constraints;
- `u*w = v**2` provides a strong exact filter;
- a conceptual simultaneous modular embedding has fixed dimension near nine before any optional embedding coordinate.

The expected work is therefore big-integer arithmetic, rank-two reduction, and low-dimensional lattice reduction/enumeration rather than exponential enumeration of the original coefficient space.

This is a structural feasibility argument for this bounded-hint construction, not a claim of a general polynomial-time RSA factoring method.

## 10. Add checks immediately after each transformation

Useful checks from the exercise include:

- Public instance: positivity, bit lengths, `gcd(n,h_i)`, pairwise `gcd(h_i,h_j)`.
- Kernel: `r.h == 0`, `s.h == 0`, full-kernel cross-product criterion, unimodularity, reduction correctness, nonzero minors.
- Bounds: derive from actual minors, not heuristic scale.
- Lifting: `u*w == v*v` and coordinate-bound checks.
- Determinants: ordered-pair sign reversal and square consistency.
- Modular rows: exactly six rows in the intended order, canonical coefficients modulo each modulus.
- Residues: `0 <= residue <= B**2`.
- Synthetic tests: use small primes and known coefficient rows so every hidden value is known; verify all six residues equal exact `A_i`.
- Public tests: exercise construction and bounds without assuming any secret values.

Step 3C1’s synthetic tests are especially reusable because they expose sign, pair ordering, and modular-inverse mistakes before any hard enumeration.

## 11. Reject unverified candidates aggressively

A short lattice vector is only a candidate.

For a lifted candidate require:

- `u*w == v**2`;
- `u,w` perfect squares when reconstructing `lambda,mu`;
- signs satisfying `v = lambda*mu`;
- reconstructed `d = lambda*r + mu*s`;
- exact `d.h == 0`;
- every `|d_ij| <= B**2`.

For each usable `i`, derive `A_i` independently from both other hints and require the two exact ordinary integers to agree and lie in `[0,B**2]`.

Do not retain candidates merely because they are short, approximately fit, or produce small residues. Exact identities are cheap compared with search and should be mandatory filters.

## 12. Use reversible algebra instead of factoring intermediate products

Once an exact

`A_i = a_i*b_i`

is known, compute

`Delta_i = h_i**2 - 4*A_i*n`.

The derivation gives the exact identity

`Delta_i = (a_i*p - b_i*q)**2`.

A correct candidate therefore requires `Delta_i >= 0` and a perfect square. If

`S_i = sqrt(Delta_i)`,

then `h_i + S_i` and `h_i - S_i` are, in some order,

`2*a_i*p` and `2*b_i*q`.

A gcd with `n` can reveal a nontrivial factor. This reversal is preferable to attempting to factor the potentially large product `A_i`.

Any proposed factors must satisfy:

- `1 < p,q < n`;
- `p*q == n`;
- sizes compatible with 1024-bit prime generation;
- optionally, local primality checks.

## 13. Verify reconstruction all the way back to the generator

After recovering `p,q`, recover each original coefficient exactly:

`a_i = h_i * p^(-1) mod q`

and

`b_i = h_i * q^(-1) mod p`.

Because `B < p,q`, the least nonnegative residues are the exact bounded coefficients.

Then verify for all three hints:

- `0 <= a_i,b_i <= B`;
- `h_i == a_i*p + b_i*q`;
- `A_i == a_i*b_i`;
- `d_ij == a_i*b_j - a_j*b_i`.

This generator-level reconstruction is stronger than checking only `p*q == n`: it proves the recovered factors and coefficients jointly explain every published hint.

Only after all these identities pass should RSA decryption be performed. Then verify `gcd(e,phi(n)) == 1` and finally re-encrypt the recovered plaintext integer to require

`m**e mod n == c`.

## Reusable procedure

**Classify the structured primitive -> inventory every input, operation, variable, and output -> map independent data-flow paths -> derive exact invariants -> reduce dimension -> derive rigorous concrete bounds -> lift only when it linearizes useful expressions -> preserve all modular semantics and residue bounds -> split the work into independently testable micro-steps -> estimate concrete complexity before enumeration -> validate each transformation on synthetic and public structure -> enumerate only in the reduced fixed-dimensional space -> reject candidates with exact filters -> reverse through exact algebraic identities -> reconstruct original hidden variables -> verify every source equation -> perform the final cryptographic operation last.**

The central lesson is that reduction and lattice methods may generate plausible candidates, but correctness comes from a chain of exact, independently checkable equalities and full reconstruction back to the generator.
