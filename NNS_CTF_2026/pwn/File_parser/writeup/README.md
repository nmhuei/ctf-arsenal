# Writeup: File parser

| Property | Value |
| :--- | :--- |
| **Category** | `pwn` |
| **Points** | `500` |
| **Author** | `Kriz` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

I wrote this custom file format parser in C! a friend of mine said something about a "boffer underflow" or something, but thankfully i implemented security measures to ensure that no one can submit illegitimate files anyway

> [!NOTE]
> The flag is located at `/flag.txt`



---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `pwn`
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
