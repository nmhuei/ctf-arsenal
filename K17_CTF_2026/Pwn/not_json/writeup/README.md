# Writeup: not json

| Property | Value |
| :--- | :--- |
| **Category** | `Pwn` |
| **Points** | `216` |
| **Author** | `-` |
| **Solves** | `34` |

---

## 📝 Challenge Overview

JSON is way too complex, so I made my own subset of it.

Connection command: `nc chal.secso.cc 4003`

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `chal.secso.cc:4003`
- Category: `Pwn`
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
