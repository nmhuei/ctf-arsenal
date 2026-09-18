# Writeup: Dead Letter

| Property | Value |
| :--- | :--- |
| **Category** | `Pwnable` |
| **Points** | `48` |
| **Author** | `-` |
| **Solves** | `118` |

---

## 📝 Challenge Overview

<p>A <a href="/tasks/dead-letter-queue_b8dacfd42cdadda3d61139356adf6267e8aeed9d.txz"><strong>queue</strong></a> where lost messages go to panic quietly.</p>
<p><code>nc 91.107.187.160 18111</code></p>
<p><code>nc 91.107.183.101 18111</code></p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 91.107.187.160 18111
nc 91.107.183.101 18111`
- Category: `Pwnable`
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

- Status: `- [ ] Solved`
- Flag: `FLAG{...}`
