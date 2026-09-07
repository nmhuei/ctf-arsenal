# Writeup: Patch Tuesday

| Property | Value |
| :--- | :--- |
| **Category** | `rev` |
| **Points** | `383` |
| **Author** | `hoover` |
| **Solves** | `6` |

---

## 📝 Challenge Overview

New to reverse engineering? This beginner challenge is an introduction to
dynamic debugging and patching Windows programs.

The provided `x86-64` `.exe` promises a free flag, but it does not behave the
way we want. Open it in a debugger such as x64dbg or IDA Free, run it, and
step through the code that decides whether you receive the flag. Watch how
the program compares values and follows a conditional jump.

Try changing that jump while debugging, or patch the instruction in the
executable and run your modified file again. Your goal is to make the
program follow the path that produces the expected behavior.



---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `rev`
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
