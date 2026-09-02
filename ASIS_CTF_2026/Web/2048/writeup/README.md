# Writeup: 2048

| Property | Value |
| :--- | :--- |
| **Category** | `Web` |
| **Points** | `146` |
| **Author** | `-` |
| **Solves** | `29` |

---

## 📝 Challenge Overview

<p>Are you good @ 2048?</p>
<p><code>91.107.164.78:8080</code></p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 91.107.164.78 8080`
- Category: `Web`
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
