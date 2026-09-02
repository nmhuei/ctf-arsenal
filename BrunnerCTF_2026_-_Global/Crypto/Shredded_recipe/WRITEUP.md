# Writeup: Shredded recipe (BrunnerCTF 2026 - Global)

- **Challenge**: Shredded recipe
- **Category**: Crypto
- **Difficulty**: Hard
- **Points**: 100
- **Path**: `/home/light/Workspace/CTF/BrunnerCTF_2026_-_Global/Crypto/Shredded_recipe`
- **Status**: ✅ SOLVED
- **Flag**: `brunner{i_really_love_solving_equations_with_lattices}`
- **Solver**: `gpt` via SageMath LLL (Kannan embedding)

---

## 1. Challenge Overview
We are given a linear congruence modulo a 512-bit prime $p$:
$$a x + b y + c z \equiv d \pmod p$$

Where $x, y, z$ are formed by slicing a 54-byte flag into 3 interleaved byte slices:
- $x = \text{bytes\_to\_long}(flag[0::3])$ (18 bytes, $x < 2^{144}$)
- $y = \text{bytes\_to\_long}(flag[1::3])$ (18 bytes, $y < 2^{144}$)
- $z = \text{bytes\_to\_long}(flag[2::3])$ (18 bytes, $z < 2^{144}$)

Because $x, y, z < 2^{144} \ll p$ ($512$ bits), this is an instance of the **Hidden Linear Form / Small Inverse / CVP** problem.

---

## 2. Mathematical Vulnerability & Kannan Embedding

We want to find small integers $(x, y, z)$ and $k$ such that:
$$a x + b y + c z - k p = d$$

We construct the 5-dimensional Kannan embedding lattice with scaling factor $S = 2^{512 - 144} = 2^{368}$ and bound $X = 2^{144}$:
$$
M = \begin{pmatrix}
S \cdot p & 0 & 0 & 0 & 0 \\
S \cdot a & 1 & 0 & 0 & 0 \\
S \cdot b & 0 & 1 & 0 & 0 \\
S \cdot c & 0 & 0 & 1 & 0 \\
S \cdot (-d) & 0 & 0 & 0 & X
\end{pmatrix}
$$

When we compute the linear combination with coefficients $(-k, x, y, z, 1)$:
$$(-k, x, y, z, 1) \cdot M = (S(a x + b y + c z - k p - d), x, y, z, X) = (0, x, y, z, X)$$

The norm of this vector is:
$$\|(0, x, y, z, X)\| = \sqrt{x^2 + y^2 + z^2 + X^2} \le 2 \times 2^{144}$$

Since the expected length of arbitrary vectors in the lattice is roughly:
$$\det(M)^{1/5} = (S^4 \cdot p \cdot X)^{1/5} = (2^{368 \times 4 + 512 + 144})^{1/5} = 2^{425.6} \gg 2^{144}$$

The target vector $(0, x, y, z, X)$ is extraordinarily short compared to the rest of the lattice. Applying the **Lenstra–Lenstra–Lovász (LLL)** algorithm reduces the lattice and isolates this row immediately.

---

## 3. Solver Implementation (solve.sage)

```python
from sage.all import *

S = 2^368
X = 2^144

p, a, b, c, d = map(int, open("crypto_shredded-recipe/output.txt").read().split())

M = Matrix(ZZ, [
    [S*p,    0, 0, 0, 0],
    [S*a,    1, 0, 0, 0],
    [S*b,    0, 1, 0, 0],
    [S*c,    0, 0, 1, 0],
    [S*(-d), 0, 0, 0, X],
])

for r in M.LLL().rows():
    if abs(r[4]) == X:
        sign = 1 if r[4] == X else -1
        x = sign * r[1]
        y = sign * r[2]
        z = sign * r[3]
        xb = int(x).to_bytes(18, "big")
        yb = int(y).to_bytes(18, "big")
        zb = int(z).to_bytes(18, "big")
        flag = b"".join(bytes([xb[i], yb[i], zb[i]]) for i in range(18))
        open("flag.txt", "wb").write(flag)
        print("FLAG:", flag.decode())
        break
```

---

## 4. Execution & Result
Executed by tool `gpt` via SageMath in under **1 second**:
```text
FLAG: brunner{i_really_love_solving_equations_with_lattices}
```
