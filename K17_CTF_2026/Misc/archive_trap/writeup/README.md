# Writeup: archive trap

| Property | Value |
| :--- | :--- |
| **Category** | `Misc` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `167` |

---

## 📝 Challenge Overview

You have broken into a secret archive in UNSW and found a exposed flag in `/win/flag.txt`, but a developer spent all night writing a input sanitiser to stop us. Can you try to read it?

Connection command: `nc chal.secso.cc 3000`

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `chal.secso.cc:3000`
- Category: `Misc`
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
