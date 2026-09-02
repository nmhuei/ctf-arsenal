# [ASIS CTF Quals 2026] Crypto - Fence

- **Category:** Crypto
- **Points:** 64 pts
- **Solves:** 80 solves
- **Status:** Solved ✅

---

## 1. Challenge Overview

The challenge implements a lattice-based encryption scheme over the polynomial quotient ring:
$$R_q = \mathbb{Z}_q[x] / (x^n + 1)$$
with parameters:
- $n = 128$
- $q = 268435361$ ($2^{28} - 175$)
- $w = 80$
- $r = 5$ (5 XOR secret shares of the flag)

### Key Generation & Encryption
For each share $idx \in [0, 4]$:
1. Small ternary polynomials $a, b \in \{-1, 0, 1\}^n$ are generated with Hamming weight $w = 80$ (40 ones, 40 negative ones, 48 zeros).
2. The public key is computed as:
   $$h = b \cdot a^{-1} \pmod{x^n + 1, q} \iff a \cdot h \equiv b \pmod{x^n + 1, q}$$
3. The encryption key $k$ is derived canonically from all cyclic rotations of $(a, b)$:
   $$k = \text{SHA3-256}(d \parallel s \parallel \min_{i} (\text{sh}(a, i) \parallel \text{sh}(b, i)))$$
4. A share $m_i$ is encrypted using SHAKE256 keystream and authenticated with HMAC-SHA256.
5. The final flag is the XOR sum of all 5 shares:
   $$\text{Flag} = m_0 \oplus m_1 \oplus m_2 \oplus m_3 \oplus m_4$$

---

## 2. Vulnerability & Mathematical Analysis

The relation $a \cdot h \equiv b \pmod{x^n + 1, q}$ is an instance of the **NTRU Short Vector Problem (uSVP)**.

Let $H$ be the $n \times n$ negacyclic rotation matrix representing multiplication by $h(x)$ in $R_q$:
Row $i$ of $H$ is $\text{sh}(h, i) = x^i \cdot h(x) \pmod{x^n + 1}$.

Then the polynomial multiplication translates directly to vector-matrix multiplication:
$$a \cdot H \equiv b \pmod q \implies a \cdot H - k \cdot q = b \quad (k \in \mathbb{Z}^n)$$

### Lattice Formulation
Construct the $(m + n) \times (m + n)$ integer lattice basis matrix using $m = 48$ equations:
$$M = \begin{pmatrix} q I_m & 0 \\ H_{:, 0..m-1} & I_n \end{pmatrix}$$

Any integer vector $( -k_{0..m-1}, a ) \in \mathbb{Z}^{m+n}$ multiplied with $M$ yields:
$$(-k, a) \cdot M = (b_{0..m-1}, a)$$

### Target Norm vs. Gaussian Heuristic
- **Target Vector Norm:**
  $$\|(b_{0..m-1}, a)\|_2 = \sqrt{\sum_{i=0}^{m-1} b_i^2 + \sum_{j=0}^{n-1} a_j^2} \approx \sqrt{48 \cdot \frac{80}{128} + 80} = \sqrt{30 + 80} = \sqrt{110} \approx \mathbf{10.49}$$
- **Gaussian Heuristic Shortest Vector for $m=48, n=128$ (dim 176):**
  $$\sigma \approx \sqrt{\frac{176}{2\pi e}} \cdot q^{48/176} \approx 3.21 \cdot (2.68 \times 10^8)^{0.2727} \approx 3.21 \times 203 \approx \mathbf{651}$$
- **Gap:**
  $$\text{Gap} = \frac{651}{10.49} \approx \mathbf{62}$$

A gap of $62$ in dimension 176 makes the target vector a uniquely identifiable shortest vector.

---

## 3. Exploitation & Solution

1. For each share $idx \in [0, 4]$:
   - Construct the $176 \times 176$ lattice matrix $M$ using $m = 48$ and $n = 128$.
   - Reduce the basis with `LLL` followed by `BKZ-20` using `fpylll`.
   - Extract the recovered short vector $a \in \{-1, 0, 1\}^n$.
   - Compute $b = a \cdot h \pmod{x^n + 1, q}$ centered into $[-q/2, q/2]$.
   - Decrypt the share $m_{idx}$ using the challenge's `dc(a, b, h, c)` routine.
2. XOR all 5 decrypted shares to recover the flag.

Execution time: **~35 seconds total** for all 5 shares.

---

## 4. Flag

```
ASIS{qu4ntum_c0h3r3nc3_1n_0v3r5tr3tch3d_h4rm0n1c_f13ld5!}
```
