# Formal Discrete Optimization & Hash Commitment Inversion Task

We are investigating a structured multi-slot preimage and state assignment problem over a discrete domain.

## 1. Formal Mathematical Problem

We consider a composite system with $N = 6$ independent input slots, indexed by $s \in \{0, 1, 2, 3, 4, 5\}$.
Each slot $s$ can be configured into one of $K = 16$ discrete states (variants), indexed by $v_s \in \{0, 1, \dots, 15\}$.

The candidate search space is the Cartesian product:
$$\mathcal{V} = \{0, \dots, 15\}^6, \quad |\mathcal{V}| = 16^6 = 2^{24} = 16,777,216.$$

For each slot $s$ and each variant state $v \in \{0, \dots, 15\}$:
- There is an associated 4-dimensional integer response vector (logits):
  $$L(s, v) = \big(l_{s, v, 0}, \, l_{s, v, 1}, \, l_{s, v, 2}, \, l_{s, v, 3}\big) \in \mathbb{Z}^4.$$
- This vector is produced by a linear affine transformation from a 12-dimensional quantized embedding vector $e(s, v) \in [-16, 16]^{12}$:
  $$L(s, v) = W \cdot e(s, v) + b,$$
  where $W \in \mathbb{Z}^{4 \times 12}$ and $b \in \mathbb{Z}^4$ are fixed published integer constants (given in `instance.json`).

### Commitment Function
Given a 32-byte session seed $S$ and fixed domain prefix $D = \text{"residuegate-six-way-logit-commitment-v1\0"}$, the commitment $C \in \{0, 1\}^{256}$ of a tuple $\vec{v} = (v_0, v_1, v_2, v_3, v_4, v_5)$ is defined by SHA-256 over the canonical byte serialization:

$$\text{message} = D \,\|\, S \,\|\, \prod_{s=0}^5 \Big( \text{u8}(s) \,\|\, \text{u8}(v_s) \,\|\, \text{le64}(l_{s, v_s, 0}) \,\|\, \text{le64}(l_{s, v_s, 1}) \,\|\, \text{le64}(l_{s, v_s, 2}) \,\|\, \text{le64}(l_{s, v_s, 3}) \Big)$$

$$C(\vec{v}) = \text{SHA256}(\text{message}).$$

We are given a specific target commitment hash $C_{\text{target}}$ and seed $S$ in `instance.json`.

---

## 2. Oracle Resources & Constraints

1. **Affine Weights**: $W \in \mathbb{Z}^{4 \times 12}$ and $b \in \mathbb{Z}^4$ are fully known.
2. **Homomorphic Evaluation Oracle**:
   - The system exposes an evaluation oracle that evaluates $W \cdot m + b$ over ciphertexts under an RLWE ring $\mathbb{Z}_q[x]/(x^N + 1)$ with $q = 167772161, N = 64$.
   - The secret key $s \in \{-3, 0, 3\}^{64}$ has already been completely recovered (available in `instance.json`).
   - The oracle accepts at most 16 evaluation queries.
3. **Reference Data**:
   - `instance.json` contains a complete reference table of 16 variant embeddings and their exact resulting logits for a benchmark baseline slot.

---

## 3. Objective & Deliverables

1. Analyze the mathematical formulation in `instance.json`.
2. Determine how the 16-query budget can be strategically utilized, or whether an algebraic invariant / reduction allows recovering the 6-tuple $\vec{v} = (v_0, \dots, v_5) \in \{0..15\}^6$ that satisfies $C(\vec{v}) = C_{\text{target}}$.
3. Write a self-contained Python script `solve_assignment.py` in this directory to compute and verify the tuple.
4. Output the result into `solution.json`:
   ```json
   {
     "status": "solved",
     "tuple": [v0, v1, v2, v3, v4, v5],
     "verification_hash_match": true
   }
   ```
