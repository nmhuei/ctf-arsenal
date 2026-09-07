# Writeup: 1+1

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `50` |
| **Author** | `minipif` |
| **Solves** | `351` |
| **Status** | `Completed` |

---

## 📝 Challenge Overview

The challenge provides a Sage script `chall.sage` and its generated output `output.py`. The flag is converted to an integer $p$ (around 512 bits), which acts as an approximate common divisor across 10 generated integers:
$$x_i = p \cdot q_i + r_i \quad (0 \le i < 10)$$
where:
- $p = \text{bytes\_to\_long}(\text{flag}) \approx 2^{512}$
- $q_i = \text{getPrime}(512) \approx 2^{512}$
- $r_i = \text{random.randint}(1, 2^{444}) < 2^{444}$

We are given only the 10 values $x_0, x_1, \dots, x_9$.

---

## 🔍 Mathematical Analysis

This is an instance of the **Approximate Common Divisor Problem (ACDP)**, specifically solvable via **Simultaneous Diophantine Approximation** using lattice basis reduction (LLL).

Notice that for each $i \ge 1$:
$$\frac{x_i}{x_0} = \frac{p q_i + r_i}{p q_0 + r_0} \approx \frac{q_i}{q_0}$$
Multiplying out the terms:
$$q_0 x_i - q_i x_0 = q_0 (p q_i + r_i) - q_i (p q_0 + r_0) = q_0 r_i - q_i r_0$$

Since $q_i \approx 2^{512}$ and $r_i < 2^{444}$:
$$|q_0 r_i - q_i r_0| < 2^{512 + 444} = 2^{956}$$
Meanwhile, each sample $x_i \approx p \cdot q_i \approx 2^{1024}$. The relation $q_0 x_i - q_i x_0$ cancels out the high-order $1024 - 956 = 68$ bits!

---

## 📐 Lattice Construction

We construct a $10 \times 10$ integer lattice basis $M$:

$$M = \begin{pmatrix}
W & C \cdot x_1 & C \cdot x_2 & \cdots & C \cdot x_9 \\
0 & -C \cdot x_0 & 0 & \cdots & 0 \\
0 & 0 & -C \cdot x_0 & \cdots & 0 \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
0 & 0 & 0 & \cdots & -C \cdot x_0
\end{pmatrix}$$

Multiplying $M$ by the integer vector $\mathbf{u} = (q_0, q_1, q_2, \dots, q_9)$ yields:
$$\mathbf{v} = \mathbf{u} \cdot M = \Big(q_0 W,\; C(q_0 x_1 - q_1 x_0),\; C(q_0 x_2 - q_2 x_0),\; \dots,\; C(q_0 x_9 - q_9 x_0)\Big)$$

Choosing weights:
- $W = 2^{512}$ (to balance the size of $q_0 W \approx 2^{1024}$)
- $C = 2^{70}$ (scaling the small error terms so $C |q_0 r_i - q_i r_0| \approx 2^{70 + 956} = 2^{1026}$)

The target vector $\mathbf{v}$ has norm $\|\mathbf{v}\| \approx \sqrt{10} \cdot 2^{1026}$.
In contrast, by Minkowski's bound, an arbitrary vector in the lattice has expected norm:
$$\det(M)^{1/10} = \big(W \cdot (C x_0)^9\big)^{1/10} \approx \big(2^{512} \cdot 2^{9 \times (70 + 1024)}\big)^{1/10} \approx 2^{1035}$$

Because $\|\mathbf{v}\|$ is significantly shorter than the average lattice vector, LLL reduction quickly finds $\mathbf{v}$ in the reduced basis.

Once $\mathbf{v}$ is obtained:
1. Extract $q_0 = |v_0 / W|$.
2. Recover $p = x_0 // q_0$.
3. Decode `long_to_bytes(p)` to retrieve the ASCII flag.

---

## 💻 Solver Implementation

The SageMath solver [`../solver/solve.sage`](../solver/solve.sage):

```python
import sys, os
from Crypto.Util.number import long_to_bytes

chall_dir = "/home/light/Workspace/CTF/TFC_CTF_2026/Crypto/1+1/challenge"
sys.path.insert(0, chall_dir)
import output

xs = output.xs
n = len(xs)
x0 = xs[0]

W = 2^512
C = 2^70

M = Matrix(ZZ, n, n)
M[0, 0] = W
for i in range(1, n):
    M[0, i] = C * xs[i]
    M[i, i] = -C * x0

L = M.LLL()

for row in L:
    if row[0] % W == 0 and row[0] != 0:
        q0 = abs(row[0] // W)
        p_cand = x0 // q0
        try:
            flag = long_to_bytes(p_cand).decode()
            if flag.startswith("TFCCTF{"):
                print("FOUND FLAG:", flag)
                with open("../flag.txt", "w") as f:
                    f.write(flag + "\n")
                break
        except Exception:
            pass
```

---

## 🚩 Flag

```
TFCCTF{nice_crypto_skillz_kid_you_will_be_great_one_day_af56c3}
```
