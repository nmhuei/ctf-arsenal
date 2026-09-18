# Writeup: QFilter

| Property | Value |
| :--- | :--- |
| **Category** | `Pwnable` |
| **Points** | `44` |
| **Author** | `-` |
| **Solves** | `133` |

---

## 📝 Challenge Overview

<p>Need a custom <a href="/tasks/QFilter_c9b8d86ebc59fcd1d7b9bf68ce3d9cb7b0f0f476.txz"><strong>Filter</strong></a>? Please be my guest.</p>
<p><code>nc 65.109.208.46 1337</code></p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 65.109.208.46 1337`
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
