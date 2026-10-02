# Writeup: Kuiper Belt Relay Core

| Property | Value |
| :--- | :--- |
| **Category** | `PWN` |
| **Points** | `38` |
| **Author** | `-` |
| **Solves** | `61` |

---

## 📝 Challenge Overview

The Relay rebooted an old diagnostic process — it just echoes back whatever you send it. Simple by design.

But it's still carrying dead code from before the blackout: a function that's never called, sitting untouched in memory. Redirect the program into it.

Connection string: nc 34.116.80.78 9998
Flag Format : CSSCTF{...}

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `PWN`
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
