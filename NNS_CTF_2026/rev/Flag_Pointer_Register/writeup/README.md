# Writeup: Flag Pointer Register

| Property | Value |
| :--- | :--- |
| **Category** | `rev` |
| **Points** | `220` |
| **Author** | `hoover` |
| **Solves** | `19` |

---

## 📝 Challenge Overview

New to reverse engineering? This beginner challenge is an introduction to
the Windows x64 calling convention and how arguments are passed in
registers.

The provided `x86-64` `.exe` decodes the flag successfully, yet it still
prints the wrong message. Somewhere between the decoder and `WriteFile`,
a perfectly good pointer ends up in the wrong place.

Open it in a debugger such as x64dbg or IDA Free and follow the final
function calls. Watch the value returned in `RAX`, then inspect how `RCX`,
`RDX`, `R8`, and `R9` are prepared before the output call.

Put the correct pointer into the register where `WriteFile` expects its
buffer. Repair it live in the debugger and step through the program again.



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
