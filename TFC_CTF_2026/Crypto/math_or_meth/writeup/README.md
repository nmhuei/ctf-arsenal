# Writeup: math or meth?

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `50` |
| **Author** | `minipif` |
| **Solves** | `202` |
| **Status** | `Completed` |

---

## 📝 Challenge Overview

The challenge provides `chall.py` and output log `output.py`. 
A secret message is converted to base-33 digits:
$$x = \text{bytes\_to\_long}(msg)$$
$$\text{row} = \big[x \pmod{33},\; (x // 33) \pmod{33},\; \dots\big]$$
The length of this decomposition is $m = 88$.

A random $n \times m$ matrix $A$ ($n = 57$) is created where all entries are chosen uniformly in $[0, 32]$. One randomly chosen row of $A$ is replaced with the secret $\text{row}$.

A prime $p$ (1084 bits) is generated, alongside random secret multipliers $a_0, a_1, \dots, a_{n-1} \in \mathbb{F}_p$.
The challenge outputs the linear combination vector $\mathbf{h} \in \mathbb{F}_p^m$:
$$h_j = \sum_{i=0}^{n-1} a_i A_{i, j} \pmod p \quad (0 \le j < m)$$
along with $n = 57, m = 88, B = 32, p$.

In matrix form:
$$\mathbf{h} = \mathbf{a}^T A \pmod p$$

---

## 🔍 Vulnerability & Mathematical Formulation

This problem is a matrix-vector knapsack / Hidden Subset Sum variant with a planted vector.

### 1. Orthogonal Lattice (Nguyen-Stern Technique)
Consider the lattice of integer vectors orthogonal to $\mathbf{h}$ modulo $p$:
$$L_p^\perp(\mathbf{h}) = \left\{ \mathbf{w} \in \mathbb{Z}^m \;\middle|\; \mathbf{w} \cdot \mathbf{h} \equiv 0 \pmod p \right\}$$

Notice that for any vector $\mathbf{w} \in \mathbb{Z}^m$ in the integer right kernel of $A$ (i.e., $A \mathbf{w} = \mathbf{0}$):
$$\mathbf{h} \cdot \mathbf{w} = (\mathbf{a}^T A) \mathbf{w} = \mathbf{a}^T (A \mathbf{w}) = \mathbf{a}^T \mathbf{0} = 0 \pmod p$$

Because $A$ has dimension $n \times m = 57 \times 88$ with $m > n$, the kernel of $A$ over $\mathbb{Q}$ has dimension:
$$\dim \ker(A) = m - n = 88 - 57 = 31$$

Since the entries of $A$ are small ($\le 32$), the kernel $\ker(A) \cap \mathbb{Z}^m$ contains vectors of very small Euclidean norm ($\|\mathbf{w}\| < 15,000$). In contrast, generic vectors in $L_p^\perp(\mathbf{h})$ have expected length:
$$\approx p^{n/m} \approx 2^{1084 \times 57 / 88} \approx 2^{702}$$

Therefore, lattice basis reduction on $L_p^\perp(\mathbf{h})$ isolates the 31 exceptionally short vectors that span $\ker(A)$.

---

## 📐 Attack Steps

### Step 1: Orthogonal Lattice Reduction via Flatter
Construct the $m \times m$ basis matrix for $L_p^\perp(\mathbf{h})$:
$$M = \begin{pmatrix}
p & 0 & 0 & \dots & 0 \\
-h_1 h_0^{-1} \pmod p & 1 & 0 & \dots & 0 \\
-h_2 h_0^{-1} \pmod p & 0 & 1 & \dots & 0 \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
-h_{m-1} h_0^{-1} \pmod p & 0 & 0 & \dots & 1
\end{pmatrix}$$

Applying LLL with the `flatter` pre-reduction library on $M$ quickly finds exactly $m - n = 31$ vectors with Euclidean norm $< 15,000$. These vectors form matrix $V \in \mathbb{Z}^{31 \times 88}$.

### Step 2: Recovering the Row Space $\Lambda$
The rows of $A$ must be orthogonal to every vector in $\ker(A)$.
Taking the integer right kernel of $V$:
$$\Lambda = \left\{ \mathbf{x} \in \mathbb{Z}^m \;\middle|\; V \mathbf{x} = \mathbf{0} \right\}$$
$\Lambda$ is a 57-dimensional lattice in $\mathbb{Z}^{88}$ that coincides with the $\mathbb{Z}$-span of the rows of $A$. We reduce $\Lambda$ via LLL (`flatter`).

### Step 3: Vectorized Babai Nearest Plane using QR
The secret $\text{row}$ is a lattice vector $\mathbf{r} \in \Lambda$ whose coordinates all lie strictly in $[0, 32]$.

To efficiently find vectors in $\Lambda \cap [0, 32]^m$:
1. Compute the QR decomposition of the reduced basis: $B^T = Q R$.
2. Generate batches of uniform target vectors $\mathbf{t} \in [0, 32]^{88}$.
3. Project each target onto $\Lambda$ using vectorized Babai Nearest Plane:
   $$\mathbf{z} = \text{round}\left( \frac{\mathbf{t} Q - \mathbf{z} R}{R_{i,i}} \right)$$
4. Filter candidate lattice points $\mathbf{p} = \mathbf{z} B$ where $0 \le p_j \le 32$ for all $0 \le j < 88$.
5. Reconstruct $x = \sum_{j=0}^{m-1} p_j \cdot 33^j$ and convert to bytes.

---

## 💻 Solver Implementation

The SageMath script [`../solver/solve.sage`](../solver/solve.sage):

```python
#!/usr/bin/env sage
import os, sys, time
import numpy as np
from Crypto.Util.number import long_to_bytes

chall_dir = '/home/light/Workspace/CTF/TFC_CTF_2026/Crypto/math_or_meth/challenge'
sys.path.insert(0, chall_dir)
import output

p, h, n, m, B = output.p, output.h, output.n, output.m, output.B
base = B + 1

# Step 1: Orthogonal Lattice Reduction via flatter
h0_inv = pow(h[0], -1, p)
rows = [[p] + [0]*(m-1)]
for j in range(1, m):
    r = [0]*m
    r[0] = (-h[j] * h0_inv) % p
    r[j] = 1
    rows.append(r)

M = Matrix(ZZ, rows)
L = M.LLL(algorithm='flatter')
short_vecs = [v for v in L.rows() if v.norm().n() < 15000]
assert len(short_vecs) == m - n

# Step 2: Compute integer kernel Lambda
V = Matrix(ZZ, short_vecs)
Lambda = V.right_kernel_matrix()
Lambda_lll = Lambda.LLL(algorithm='flatter')

# Step 3: Vectorized Babai Nearest Plane using QR
B_mat = np.array(Lambda_lll, dtype=np.float64)
dim, m_dim = B_mat.shape
Q, R = np.linalg.qr(B_mat.T)

def run_babai_batch(targets):
    tQ = targets @ Q
    N = targets.shape[0]
    z = np.zeros((N, dim), dtype=np.int64)
    for i in reversed(range(dim)):
        val = (tQ[:, i] - z[:, i+1:] @ R[i, i+1:]) / R[i, i]
        z[:, i] = np.round(val)
    return z

N = 25000
targets = np.random.uniform(0, 32, size=(N, m_dim))
z = run_babai_batch(targets)
z_unique = np.unique(z, axis=0)

Lambda_exact = Matrix(ZZ, Lambda_lll)
for zi in z_unique:
    pt = vector(ZZ, zi) * Lambda_exact
    if all(0 <= c <= 32 for c in pt):
        val = sum(int(pt[i]) * (base^i) for i in range(len(pt)))
        cand = long_to_bytes(val)
        if all(32 <= b <= 126 for b in cand) and len(cand) > 10:
            flag_str = f"TFCCTF{{{cand.decode('latin-1')}}}"
            print(f"[+] RECOVERED FLAG: {flag_str}")
            with open("../flag.txt", "w") as f:
                f.write(flag_str + "\n")
            break
```

---

## 🚩 Flag

```
TFCCTF{this_is_a_very_very_long_flag_for_a_short_ctf_chall_ggs}
```
