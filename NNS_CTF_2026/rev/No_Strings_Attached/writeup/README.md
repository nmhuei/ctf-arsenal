# Writeup: No Strings Attached

| Property | Value |
| :--- | :--- |
| **Category** | `rev` |
| **Points** | `286` |
| **Author** | `hoover` |
| **Solves** | `12` |

---

## 📝 Challenge Overview

New to reverse engineering? This beginner challenge is an introduction to
tracing the library calls a Linux program makes.

The provided `x86-64` ELF asks you to guess a passphrase. The passphrase
is the flag, but it is not written down anywhere in the file. Running
`strings` on the binary only gets you `guess:`, `correct` and `rejected`.
The program builds the real passphrase in memory first, and only then
hands it to a function in the C standard library to compare against yours.

Run the program under a library call tracer such as `ltrace` and watch the
comparison. Your goal is to read the passphrase out of the arguments the
program passes to it.



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
