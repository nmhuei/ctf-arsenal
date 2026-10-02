# Writeup: leaky rsa (K17 CTF 2026)

- **Category**: Crypto
- **Points**: 100
- **Status**: Solved ✅
- **Flag**: `K17{th3_t1tan1c_sh0uldv3_us3d_duct_t4p3}`

---

## 1. Challenge Overview
We are given:
- Modulus $N = P \times Q$ ($1024$-bit primes)
- Public exponent $e = 257$
- Leak: $d_{sum} = d_p + d_q = (d \bmod (P - 1)) + (d \bmod (Q - 1))$
- Ciphertext: $c = m^e \bmod N$

---

## 2. Algebraic Analysis
By the definition of modular inverses:
$$e \cdot d_p = k(P - 1) + 1 \quad \text{for some } 1 \le k < e$$
$$e \cdot d_q = j(Q - 1) + 1 \quad \text{for some } 1 \le j < e$$

Adding both equations:
$$e(d_p + d_q) = k(P - 1) + j(Q - 1) + 2 = kP + jQ - (k + j) + 2$$

Let $A = e \cdot \text{leak} + k + j - 2$. Then:
$$kP + jQ = A$$

Since $N = P \cdot Q$, multiplying $kP$ and $jQ$ yields:
$$(kP) \cdot (jQ) = k \cdot j \cdot N$$

Thus, $X = kP$ and $Y = jQ$ are roots of the quadratic polynomial:
$$T^2 - AT + kjN = 0$$

The discriminant is:
$$\Delta = A^2 - 4kjN$$

Since $e = 257$, there are only $256 \times 256 = 65,536$ possible integer pairs $(k, j)$. We iterate through all $(k, j)$, check if $\Delta$ is a perfect square, compute the roots $T_1, T_2$, verify divisibility by $k, j$, and check $P \cdot Q = N$.

---

## 3. Exploit Script
See [`solver/solve.py`](../solver/solve.py).
