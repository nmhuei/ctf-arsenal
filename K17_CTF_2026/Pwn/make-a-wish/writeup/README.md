# Writeup: make-a-wish

| Property | Value |
| :--- | :--- |
| **Category** | `Pwn` |
| **Points** | `151` |
| **Author** | `-` |
| **Solves** | `66` |

---

## 📝 Challenge Overview

our own make a wish program, and you dont even need to have cancer!

Connection command: `nc chal.secso.cc 4004`

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `chal.secso.cc:4004`
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
