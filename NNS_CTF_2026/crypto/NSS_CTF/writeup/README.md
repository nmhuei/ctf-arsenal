# Writeup: NSS CTF

| Property | Value |
| :--- | :--- |
| **Category** | `crypto` |
| **Points** | `500` |
| **Author** | `Zukane` |
| **Solves** | `1` |

---

## 📝 Challenge Overview

The challenge implements the revised **NTRU Signature Scheme (NSS)** over the cyclotomic ring $\mathcal{R} = \mathbb{Z}[x]/(x^{256} + 1)$ with moduli $p = 3$ and $q = 367$.
The keypair consists of secret polynomials:
- $u \in \{-1, 0, 1\}^{256}$
- $f = u + 3 f_1$, where $f_1 \in \{-1, 0, 1\}^{256}$ ($df = 88$)
- $g = u + 3 g_1$, where $g_1 \in \{-1, 0, 1\}^{256}$ ($dg = 60$)
- Public key $pk = g / f \pmod q$

AES-ECB key is derived as `key = sha256(bytes(f % 256)).digest()`.

---

## 🔍 Reconnaissance & Vulnerability Analysis

1. **Exact Cancellation of Signer Nonce ($w$)**:
   In clean signatures where the rejection vector $e = 0$ (observed at indices 2, 4, 9), we lift:
   $$F = s_{\text{cent}} + q K = f \cdot w \in \mathbb{Z}[x]/(x^{256} + 1)$$
   $$G = t_{\text{cent}} + q L = g \cdot w \in \mathbb{Z}[x]/(x^{256} + 1)$$
   $$D = \frac{G - F}{3} = \frac{(g - f) \cdot w}{3} = \Delta \cdot w$$
   where $\Delta = g_1 - f_1 \in \{-2, \dots, 2\}^{256}$.
   Taking the quotient in $\mathbb{Q}[x]/(x^{256} + 1)$:
   $$Q = \frac{F}{D} = \frac{f \cdot w}{\Delta \cdot w} = \frac{f}{\Delta}$$
   The random nonce $w$ completely cancels out, yielding the exact rational quotient $Q$.

2. **Subfield Norm & Autocorrelation Identities**:
   From the signature products, we obtain the exact Hermitian autocorrelation:
   $$J(x) = \Delta(x) \overline{\Delta(x)} \pmod{x^{256} + 1}$$
   and the exact degree 128 subfield norm polynomial:
   $$H(x) = \Delta(x) \Delta(-x) \pmod{x^{256} + 1}$$

3. **Linear Dimensionality Reduction**:
   Combining $J(x) = \Delta(x) \overline{\Delta}(x)$ and $H(x) = \Delta(x) \Delta(-x)$, we obtain the linear relation:
   $$J(x) \cdot \Delta(-x) = H(x) \cdot \overline{\Delta}(x) \pmod{x^{256} + 1}$$
   This linear constraint cuts the search space from 256 dimensions down to an exact 128-dimensional integer subspace.

4. **Fast 128-D Metric Lattice Reduction**:
   Under the metric Gram matrix $G_K = K \cdot J^{-1} \cdot K^T$ of the 128-dimensional kernel, running Flatter + BKZ-20 immediately finds a short vector with exact squared norm 2 in under 5 seconds. Factoring out the fixed subfield root $(z^i + (-1)^i z^{-i})$ yields the target vector $\Delta$ with $\|\Delta\|_2^2 = 298$ and $\|\Delta\|_\infty \le 2$.
   Finally, $f = Q \cdot \Delta$ recovers the secret key with $\|f\|_2^2 = 1705$ and $\|f\|_\infty \le 4$.

---

## 💻 Exploitation Strategy & PoC

Exploit script is located at [`../solver/solve.py`](../solver/solve.py).

```bash
python3 ../solver/solve.py
```

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `NNS{m4k3_5ur3_th3_fl4g_f0rm4t_15_NNS_n0t_NSS}`
