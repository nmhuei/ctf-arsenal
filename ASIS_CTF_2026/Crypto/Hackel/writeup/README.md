# Writeup: Hackel

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `45` |
| **Author** | `-` |
| **Solves** | `127` |

---

## 📝 Challenge Overview

<h1>🗝️ Hackel</h1>
<p>Our lead cryptographer <a href="/tasks/Hackel_167b289c63c46836d376945105d757028321303a.txz"><strong>hackel</strong></a> proudly announced a &quot;revolutionary post-quantum vault&quot; guarded by intricate algebraic group presentations.</p>
<p>With a search space boasting over <strong>1.6 quadrillion</strong> states, they confidently declared:</p>
<blockquote>
<p><em>&quot;No supercomputer on Earth could brute-force our permutations before the heat death of the universe!&quot;</em></p>
</blockquote>
<p>Well... brute force is for amateurs. Armed with a fresh cup of coffee, a notebook, and a touch of modern group theory, can you reconstruct the secret representation, unlock the vault, and claim the flag?</p>
<pre><code class="language-bash">nc 65.109.208.91 3771
</code></pre>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 65.109.208.91 3771`
- Category: `Crypto`
- Key observations & vulnerability hypothesis:
  *(Document reverse engineering, source code review, or protocol analysis here)*

---

## 💻 Exploitation Strategy & PoC

Exploit script is located at [`../solver/solve.py`](../solver/solve.py).

```bash
python3 ../solver/solve.py
```

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `FLAG{...}`
