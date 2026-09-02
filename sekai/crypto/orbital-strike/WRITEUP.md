# Writeup: orbital-strike

- **Category:** Cryptography
- **Platform:** SekaiCTF
- **Rating:** 3⟡ Hard (89 solves)
- **Status:** Solved
- **Flag:** `SEKAI{orbital_strike_like_miku_miku_beam!!!}`

---

## 1. Challenge Overview

The challenge implements two coupled Linear Congruential Generators (LCGs) with different moduli:
- **Inner LCG (`moons`)**:
  $$M_i = (a \cdot M_{i-1} + b) \pmod p$$
  where $p$ is a 311-bit prime (`0x137` bits), and $M_0 = B$.
- **Outer LCG (`planets`)**:
  $$X_i = (A \cdot X_{i-1} + M_i) \pmod P$$
  where $P$ is a 256-bit prime, and $X_0 = X$.
- We are provided with:
  - 14 outputs of the outer LCG: $\text{orbit} = [X_1, X_2, \dots, X_{14}]$.
  - AES-ECB ciphertext $\text{star} = \text{AES-ECB}(X)(\text{FLAG})$.

---

## 2. Mathematical Vulnerability & Attack Analysis

### Step 1: Eliminating the Outer Recurrence Modulo $P$
Let $D_i = X_{i+1} - X_i$ for $i = 1, \dots, 13$.
Subtracting successive equations:
$$D_i = A \cdot D_{i-1} + (M_{i+1} - M_i) - k_i P$$
Let $E_i = M_{i+1} - M_i$. The inner differences satisfy:
$$E_{i+1} \equiv a \cdot E_i \pmod p$$
Thus, the vector of differences $(D_1, \dots, D_{13})$ has linear combinations that eliminate the large terms.

### Step 2: Recovering Syzygies via LLL
Construct the Hankel-like matrix of differences:
$$H = \begin{pmatrix} D_1 & D_2 & \dots & D_{11} \\ D_2 & D_3 & \dots & D_{12} \\ D_3 & D_4 & \dots & D_{13} \end{pmatrix}$$
Using LLL on the right kernel of $H$, we find short vectors $\mathbf{r} \in \mathbb{Z}^{11}$ such that:
$$\sum_k r_k D_{k+j} \approx 0$$
These short vectors correspond to polynomials $\sum r_k T^k$ that annihilate $a \pmod p$.

### Step 3: Recovering Inner Modulus $p$ and Multiplier $a$
Taking pairs of polynomials $f_1(T), f_2(T)$ from the short syzygies, their resultant:
$$\text{Res}(f_1, f_2) \equiv 0 \pmod p$$
The greatest common divisor of these integer resultants yields a composite number containing the 311-bit prime $p$.
Factoring the GCD isolates $p$.
Then computing $\gcd(f_1(T), f_2(T)) \pmod p$ yields a linear factor $(T - a)$, revealing the inner multiplier $a$.

### Step 4: Recovering Inner Differences $E$ and Outer Modulus $P$
With $p$ and $a$ known, the relations $E_{i+1} - a E_i \equiv 0 \pmod p$ define an integer lattice over the 13 variables $E_i$ and the quotient witnesses $n_i$.
Applying LLL finds the unique short difference vector $E$.
From $E$, cross-multiplying $(D_i - E_i) D_{j-1} - (D_j - E_j) D_{i-1}$ reveals multiples of $P$. Taking their GCD exposes the 256-bit prime $P$.

### Step 5: Multiplier $A$ and Key $X$
With $P$ known:
$$A = (D_i - E_i) \cdot D_{i-1}^{-1} \pmod P$$
Then backtracking from $X_1, X_2$:
$$Y_1 = (X_2 - A X_1 - E_1) \pmod P$$
$$X = (X_1 - Y_1) \cdot A^{-1} \pmod P$$
Decrypting $\text{star}$ with AES-ECB using $X$ (32 bytes) recovers the flag.

---

## 3. Flag
`SEKAI{orbital_strike_like_miku_miku_beam!!!}`
