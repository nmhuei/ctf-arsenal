# Writeup: escapetime

| Property | Value |
| :--- | :--- |
| **Category** | `pwn` |
| **Points** | `500` |
| **Author** | `Qyn` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

WebAssembly is supposed to stay inside the sandbox, thankfully wasmtime uses rust and has a heap sandbox. That will keep us safe!

> [!NOTE]
> This is a 0day challenge and we are hoping you keep th{is|ese} 0day{|s} to yourself until the vulnerabilit{y|ies} {is|are} patched.



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
