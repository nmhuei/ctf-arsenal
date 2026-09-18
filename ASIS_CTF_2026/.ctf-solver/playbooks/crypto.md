# crypto Operational Playbook (SOP)

## 1. Reconnaissance & Discriminating Checks
1. **Metadata & Telemetry Profiling**:
   - Inspect challenge metadata, point value, and solve times before computing. Rapid initial solves (< 15 minutes) indicate direct algebraic reductions, known structural attacks, or small-parameter weaknesses rather than high-complexity custom cryptanalysis.
   - Identify all challenge artifacts: public parameters, source code, encrypted outputs, and protocol transcript files.
2. **Environment & Toolchain Audit**:
   - Verify execution environments immediately: check interpreter binaries (`python3`, dedicated virtual/conda environments for SageMath), native accelerators (`flatter`, `fplll`), and supporting assets (e.g., BKZ strategy configuration JSONs).
   - Resolve imports and library paths explicitly to avoid runtime failures midway through long computations.
3. **Primitive & Algebraic Structure Classification**:
   - Map problem primitives into mathematical abstractions:
     - *Ring/Lattice*: Identify polynomial quotient rings $\mathbb{Z}_q[X]/(f(X))$, quotient polynomial degrees, cyclotomic properties, and modulus-to-dimension ratios.
     - *Group/Curve*: Identify field characteristics, group orders, factorization of curve orders (smoothness, CM discriminant, embedding degrees).
     - *Symmetric/Stream*: Check state sizes, linear feedback polynomials, S-box algebraic degrees, and nonce reuse.
4. **Discriminant Metric Computation**:
   - For lattices: Calculate the lattice determinant, dimension $d$, Gaussian heuristic expected norm $\sigma_{GH}(L)$, and target secret norm $\|\mathbf{v}\|$. Determine the gap ratio $\gamma = \sigma_{GH}(L) / \|\mathbf{v}\|$. A large gap ($\gamma \gg 1$) proves uSVP / overstretched regime suitability.
   - For RSA/Factoring: Check small prime factors, Fermat distance $|p - q|$, Wiener/Boneh-Durfee bounds, and common divisors across instances.

---

## 2. Hypothesis Triage & Dead-End Pruning
1. **Subspace & Ideal Lattice Module Recognition**:
   - If initial reduction (LLL/`flatter`) outputs vectors substantially shorter than random vectors ($O(q)$) but larger than the target secret vector, do not discard the basis as failed. Recognize that reduction has isolated the underlying ideal submodule $R \cdot \mathbf{v}$.
   - Separate the basis vectors into the low-norm submodule ($d' \ll d$) and the orthogonal lattice, pruning the latter completely from subsequent reduction stages.
2. **Algebraic Invariance & Orbit Exploitation**:
   - Identify symmetry groups acting on valid keys (e.g., negacyclic rotations $X^k$, automorphisms, unit groups $\mathcal{O}_K^\times$).
   - If symmetric key derivation or decryption relies on canonical orbit representatives (e.g., lexicographical minimums over shifts), verify whether recovering any element in the orbit suffices. Avoid brute-forcing the exact unrotated secret if canonicalization absorbs the transformation.
3. **Pruning High-Complexity Direct Reductions**:
   - Terminate attempts to run high-block-size BKZ ($\beta \ge 40$) on large composite dimensions ($d \ge 200$) without structural decomposition or projection.
   - If a polynomial system has high degree and many variables without sparsity or relinearization anchors, prune direct Gröbner basis computations and check for hidden linear relationships or fault injection opportunities.

---

## 3. Local Verification & Sandbox Testing
1. **Progressive Two-Stage Reduction Pipeline**:
   - **Stage 1 (Submodule Isolation):** Execute fast integer lattice reduction (`flatter` or optimized LLL) over the complete basis to isolate the target submodule spanning the secret ideal.
   - **Stage 2 (Progressive Block-Size Escalation):** Extract the isolated submodule basis and apply a progressive BKZ ladder ($\beta \in [15, 20, 25, 30, 35, \dots]$) with early exit as soon as a vector matching the theoretical secret norm is encountered.
2. **Synthetic Mini-Instance Testing**:
   - Before executing compute-intensive scripts on production parameters, test the complete pipeline on synthetic miniature instances ($n/2$, smaller modulus, or synthetic keys) where the secret vector is known.
3. **Cryptographic Inversion & Local Oracle Testing**:
   - Validate decrypted candidates against challenge validation checks (e.g., HMAC-SHA256, signature verification, or authenticated padding) locally.
   - For multi-instance schemes (e.g., $k$-out-of-$k$ XOR secret sharing across multiple locks), verify each component independently before final aggregation.

---

## 4. Remote Triggering & Flag Capture
1. **Complete Offline Reconstruction First**:
   - Solve all cryptographic components locally and offline whenever challenge artifacts provide all public data. Do not interact with remote services until the mathematical reduction is completely validated.
2. **Multi-Part Secret Aggregation**:
   - Reconstruct aggregated messages (XOR sums, Shamir interpolation, CRT reconstructions) strictly within an automated solve script.
3. **Flag Format Verification & Persistence**:
   - Validate candidate flag bytes against known event regex formats (`^[a-zA-Z0-9_]+{[!-~]+}$`) and check for clean ASCII printable characters.
   - Save the final recovered flag to `flag.txt` in the root challenge workspace immediately upon recovery.

---

## 5. Formal & Mathematical Escalation (ctf-ask Triggers)
Escalate to formal symbolic abstraction or specialized solvers when:
1. **High-Degree Multivariate Polynomial Systems**:
   - Algebraic equations over finite fields where relinearization fails and standard Gröbner basis routines (`sage.rings.polynomial.toy_buchberger` or Singular) exceed time limits.
2. **Complex Lattice Embeddings with Non-Uniform Noise**:
   - Hidden Number Problems (HNP), inhomogeneous short integer solution (ISIS), or learning with errors with non-spherical noise distributions requiring specific Kannan embedding weight tuning.
3. **Isogeny & Endomorphism Ring Computations**:
   - Elliptic curve challenges requiring quaternion algebra representations, maximal order endomorphism ring computations, or high-degree isogeny walks beyond standard Vélu formulas.
4. **Arbitrary Bit-Level Arithmetic Constraints**:
   - Mixed Boolean-Arithmetic (MBA) expressions, ARX combinations (Addition, Rotation, XOR), or non-linear keystream generators requiring translation into formal SAT/SMT (Z3, Bitwuzla) theories.

---

## 6. Procedural Traps to Avoid
1. **The Static BKZ Parameter Trap**:
   - *Trap:* Hardcoding a fixed block size (e.g., $\beta = 25$) that solved one instance, causing the solver to fail on subsequent instances whose basis geometries require $\beta = 30$ or $35$.
   - *Fix:* Always implement an adaptive progressive search loop over block sizes with dynamic norm termination conditions.
2. **Full-Basis Brute-Force Reduction**:
   - *Trap:* Running expensive reduction algorithms directly on the combined $(2n \times 2n)$ basis instead of decoupling the orthogonal components.
   - *Fix:* Use fast LLL/`flatter` as a dimensionality-reduction filter to extract the lower-dimensional submodule before applying BKZ.
3. **Environment & Script Invocation Drift**:
   - *Trap:* Running Sage scripts via generic Python interpreters or running Python scripts via `sage` without handling entrypoint differences (`__main__` vs `sage.all`).
   - *Fix:* Explicitly invoke the target environment interpreter (`/path/to/sage/bin/python`) and explicitly handle script path additions (`sys.path.insert`).
4. **Polling & Spin-Locking Antipattern**:
   - *Trap:* Polling background task statuses in tight loops or using shell sleep commands, risking rate limits and context clutter.
   - *Fix:* Use platform-native scheduling or wait for asynchronous notifications from background task managers.
5. **Loss of State on Server/Session Restart**:
   - *Trap:* Assuming long-running background tasks persist indefinitely across runtime disconnects or restarts.
   - *Fix:* Make solver scripts idempotent and log progress incrementally to disk so execution can resume from the last completed instance or lock.
