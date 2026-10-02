# Writeup: Chrono II

| Property | Value |
| :--- | :--- |
| **Category** | `Cryptography` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `296` |

---

## 📝 Challenge Overview

We have again intercepted their talk and the cipher text, but this time it seems like its always changing. Help us!

"The Time is ticking, it will never stop, no one will ever decrypt it"

Flag Format: CSSCTF{...}

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `http://34.116.80.78:8001`
- Category: `Cryptography`
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
