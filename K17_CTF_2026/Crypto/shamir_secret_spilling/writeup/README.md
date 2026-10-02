# Writeup: shamir secret spilling (K17 CTF 2026)

- **Category**: Crypto
- **Points**: 100
- **Status**: Solved ✅
- **Flag**: `K17{0ur_cl1ent5_r3ally_d0nt_like_r0tating_their_keys!}`

---

## 1. Challenge Overview
- Polynomial $P(x)$ has degree $< 16$ with 16 known shares $(x_k, px_k)$.
- Polynomial $Q(x)$ has degree $< 32$ with 16 backward-compatible shares (same as known) and 8 newly issued shares $(x_j, qx_j)$.
- The secret is $\text{FLAG} = Q(0) = Q_0$.
- Relation: $|\text{centered}(Q_i - P_i)| < B$ for all $0 \le i < 32$, where $B \approx 2^{273}$ and $\text{MOD} \approx 2^{512}$.

---

## 2. Mathematical Modeling (HNP / CVP on Lattice)
Let $\Delta = Q - P_{\text{padded}} \in \mathbb{Z}^{32}$.
- $\|\Delta\|_\infty < B$.
- $Q$ satisfies 24 evaluations (16 known $+ 8$ new).
- Over $\mathbb{F}_{\text{MOD}}$, this yields an underdetermined linear system of 24 equations in 32 variables:
  $$M \cdot \Delta = y \pmod{\text{MOD}}$$
  where $M_{r, c} = x_r^c$ and $y_r = \text{eval}_r - P_{\text{padded}}(x_r) \pmod{\text{MOD}}$.

Partition $M = [A \mid B_{\text{mat}}]$ with $A \in \text{GL}_{24}(\mathbb{F}_{\text{MOD}})$. Multiplying by $A^{-1}$:
$$[I_{24} \mid W] \cdot [\Delta_{0..23} \mid \Delta_{24..31}]^T = y_{\text{target}} \pmod{\text{MOD}}$$
where $W = A^{-1} B_{\text{mat}}$ ($24 \times 8$) and $y_{\text{target}} = A^{-1} y$ ($24 \times 1$).

For the 8 variables $t = \Delta_{24..31}$:
$$\Delta_{0..23} = y_{\text{target}} - W \cdot t \pmod{\text{MOD}}$$

We construct a canonical $33 \times 33$ Kannan embedding lattice:
- 24 rows: $(\text{MOD} \cdot e_j, 0, 0)$
- 8 rows: $(-W[:, i], e_i, 0)$
- 1 row: $(y_{\text{target}}, 0, B)$

Since all coordinates of $[\Delta_{0..23}, t_{0..7}, B]$ have magnitude $< B$, LLL / `flatter` recovers $\Delta$ instantly ($< 1$ second).
$Q_0 = (P_{\text{padded}}[0] + \Delta_0) \bmod \text{MOD}$ reveals the flag.

---

## 3. Exploit Script
See [`solver/solve.py`](../solver/solve.py).
