# Writeup: Signal Race

| Property | Value |
| :--- | :--- |
| **Category** | `Pwnable` |
| **Points** | `43` |
| **Author** | `-` |
| **Solves** | `138` |

---

## 📝 Challenge Overview

<p>A paranoid VM, a badly timed <a href="/tasks/Signal_Race_5cfce154b37a7b3531fe35bd6ee161d6a5f17964.txz"><strong>signal</strong></a>, and a flag begging to escape.</p>
<p><code>nc 91.107.187.160 18121</code></p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 91.107.187.160 18121`
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
