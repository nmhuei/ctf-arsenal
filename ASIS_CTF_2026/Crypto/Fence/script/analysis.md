# Cryptographic Modeling and Reduction Analysis: Fence

## 1. Mathematical Structure & Parameters
The challenge implements a variant of the **NTRU** cryptosystem over the polynomial quotient ring:
$$R_q = \mathbb{Z}_q[X] / (X^n + 1)$$

### Parameters
- Degree $n = 128 = 2^7$ (a power of 2, so $X^n + 1 = \Phi_{256}(X)$ is irreducible over $\mathbb{Q}$)
- Modulus $q = 268435361$ (a 28-bit prime, $q \equiv 1 \pmod{32}$)
- Hamming weight $w = 80$ (dense ternary polynomials)
- Number of locks $r = 5$
- Flag reconstructed via multi-party secret sharing: $\text{flag} = m_0 \oplus m_1 \oplus m_2 \oplus m_3 \oplus m_4$

## 2. Key Generation & Cryptographic Relation
For each lock $k \in \{0, \dots, 4\}$:
- Secret polynomials $a, b \in R$ are ternary vectors sampled uniformly from $\{-1, 0, 1\}^n$, each with 40 entries equal to $+1$, 40 entries equal to $-1$, and 48 entries equal to $0$.
- Consequently:
  $$\|a\|^2 = 80, \quad \|b\|^2 = 80 \implies \|(b, a)\|^2 = 160 \implies \|(b, a)\| = \sqrt{160} \approx 12.649$$
- Public key:
  $$h \equiv b \cdot a^{-1} \pmod{X^n + 1} \pmod q$$
  Equivalently:
  $$a \cdot h \equiv b \pmod{X^n + 1} \pmod q$$
  Or in $\mathbb{Z}[X] / (X^n + 1)$:
  $$a(X) \cdot h(X) - q \cdot k(X) = b(X)$$

## 3. Lattice Modeling & The "Gap"
The challenge description explicitly hints:
> *"Five locks, one dense true fence, and a flag that thinks it is safe. Find the gap!"*

### Gaussian Heuristic vs. Target Norm
Consider the $2n = 256$-dimensional full NTRU lattice $L$:
$$L = \left\{ (y, x) \in \mathbb{Z}^{2n} : x \cdot h \equiv y \pmod{X^n + 1} \pmod q \right\}$$
Basis matrix $B \in \mathbb{Z}^{2n \times 2n}$:
$$B = \begin{pmatrix} q I_n & 0 \\ H & I_n \end{pmatrix}$$
where $H$ is the circulant representation of multiplication by $h(X) \pmod{X^n + 1}$.

- $\det(L) = q^n = q^{128}$
- Dimension $d = 2n = 256$
- Expected shortest vector by the Gaussian Heuristic:
  $$\sigma_{GH}(L) \approx \sqrt{\frac{d}{2\pi e}} \cdot (\det L)^{1/d} = \sqrt{\frac{256}{2\pi e}} \cdot \sqrt{q} \approx 3.87 \times 16384 \approx 63,400$$
- Actual target vector norm:
  $$\|(b, a)\| = \sqrt{160} \approx 12.65$$
- **The Gap**:
  $$\frac{\sigma_{GH}(L)}{\|(b, a)\|} \approx \frac{63400}{12.65} \approx 5,012$$
This massive gap ($\approx 5000$) places the instance well into the overstretched NTRU regime.

## 4. Two-Stage Reduction Strategy

Because $(b, a)$ generates an entire $n$-dimensional ideal $R \cdot (b, a)$ inside the $2n$-dimensional lattice, running basic LLL on the full $256 \times 256$ lattice tends to get stuck in the ideal around norm $\sim 95$.

However, the reduction separates cleanly into two ultrafast stages:

1. **Stage 1 (Submodule Isolation via Flatter):**
   Run `flatter` (fast LLL) on the full $256 \times 256$ basis. In $\approx 8$ seconds, `flatter` completely separates the lattice into:
   - 128 vectors of norm $\sim q \approx 2.7 \times 10^8$ (the orthogonal complement)
   - 128 vectors of norm $\sim 95$ spanning the target ideal module $R \cdot (b, a)$

2. **Stage 2 (Sublattice Reduction via BKZ):**
   Extract the 128 small basis vectors (dimension $128 \times 256$) and apply progressive BKZ with block sizes $[15, 20, 25]$ using `fpylll`.
   In $< 0.3$ seconds, BKZ-25 isolates the exact shortest vector of norm $\sqrt{160} = 12.649$.

3. **Key Recovery & Canonical Invariance:**
   The recovered vector is a rotation $\pm X^k (b, a)$.
   Because the key derivation `ky(a, b, s)` takes the lexicographical minimum over all $2n$ negacyclic shifts:
   $$\min_{0 \le i < 2n} \left( \text{sh}(a, i) \parallel \text{sh}(b, i) \right)$$
   any shift $X^k (a, b)$ yields the identical canonical symmetric key $K$.
