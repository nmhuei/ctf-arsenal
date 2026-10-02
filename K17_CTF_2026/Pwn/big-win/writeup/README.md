# Writeup: big-win

| Property | Value |
| :--- | :--- |
| **Category** | `Pwn` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `144` |

---

## 📝 Challenge Overview

i heard that 99% of gamblers walk away before winning big. i am the 99%.

Note: We've added a debugging tool on the remote to help you out a bit.
The `SNAPSHOT()` call will [magically](https://man7.org/linux/man-pages/man2/ptrace.2.html) print out a view of the program stack.
You can ignore the snapshot stuff in the code, it's just there to enable this functionality.


Connection command: `nc chal.secso.cc 4001`

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `chal.secso.cc:4001`
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
