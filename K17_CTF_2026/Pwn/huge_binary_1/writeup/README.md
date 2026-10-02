# Writeup: huge binary 1

| Property | Value |
| :--- | :--- |
| **Category** | `Pwn` |
| **Points** | `111` |
| **Author** | `-` |
| **Solves** | `105` |

---

## 📝 Challenge Overview

they say, "sir, it's the biggest binary i've ever seen", "it's the greatest binary ever made" - nobody's ever seen a bigger binary


Connection command: `nc chal.secso.cc 4002`

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `chal.secso.cc:4002`
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
