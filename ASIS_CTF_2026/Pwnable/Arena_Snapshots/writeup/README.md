# Writeup: Arena Snapshots

| Property | Value |
| :--- | :--- |
| **Category** | `Pwnable` |
| **Points** | `36` |
| **Author** | `-` |
| **Solves** | `187` |

---

## 📝 Challenge Overview

<p>A very normal <a href="/tasks/arena-snapshots_f3df2911b7bb124d34b4810d8ee87330959ae1ad.txz"><strong>arena</strong></a> manager where nothing bad can happen after you press “rollback.”</p>
<p><code>nc 91.107.187.160 18123</code></p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 91.107.187.160 18123`
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
