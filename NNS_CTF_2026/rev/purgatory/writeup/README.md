# Writeup: purgatory

| Property | Value |
| :--- | :--- |
| **Category** | `rev` |
| **Points** | `500` |
| **Author** | `hoover` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

We hot patched the validator during business hours. Nothing
crashed, which is a good sign.



---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `purgatory-66b577a4b015.chall.nnsc.tf:1337`
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
