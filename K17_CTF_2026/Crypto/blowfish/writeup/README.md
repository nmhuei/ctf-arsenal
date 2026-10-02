# Writeup: blowfish

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `121` |
| **Author** | `yellowsubmarine1447` |
| **Solves** | `93` |

---

## 📝 Challenge Overview

we've spent a gillion dollars to develop secure fish infrastructure

Connection command: `nc chal.secso.cc 2001`

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `chal.secso.cc:2001`
- Category: `Crypto`
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
