# Writeup: online-roulette

| Property | Value |
| :--- | :--- |
| **Category** | `Pwn` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `142` |

---

## 📝 Challenge Overview

live roulette players keep complaining that they dont get enough spins per hour, so we are introducing ROULETTE ONLINE!!! despite the (small) house edge, this minibolt guy keeps winning???

Note: We've added a debugging tool on the remote to help you out a bit.
The `SNAPSHOT()` call will [magically](https://man7.org/linux/man-pages/man2/ptrace.2.html) print out a view of the program stack.
You can ignore the snapshot stuff in the code, it's just there to enable this functionality.


Connection command: `nc chal.secso.cc 4000`

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `chal.secso.cc:4000`
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
