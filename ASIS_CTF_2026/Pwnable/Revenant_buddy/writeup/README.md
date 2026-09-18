# Writeup: Revenant buddy

| Property | Value |
| :--- | :--- |
| **Category** | `Pwnable` |
| **Points** | `40` |
| **Author** | `-` |
| **Solves** | `154` |

---

## 📝 Challenge Overview

<p><a href="/tasks/Revenant-Buddy_80182662e602ed9daef4d375850549d7ce547524.txz"><strong>Revenant Buddy</strong></a> is a tiny machine with a huge attitude problem. It speaks in mysterious bytes, guards its secrets like a dragon, and answers every mistake with the emotional range of a toaster.</p>
<p>‍<code>nc 91.107.151.102 18113</code></p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 91.107.151.102 18113`
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
