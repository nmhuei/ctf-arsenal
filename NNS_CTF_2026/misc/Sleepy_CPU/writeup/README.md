# Writeup: Sleepy CPU

| Property | Value |
| :--- | :--- |
| **Category** | `misc` |
| **Points** | `500` |
| **Author** | `simen` |
| **Solves** | `1` |

---

## 📝 Challenge Overview

Power analysis is a technique where the current consumption of a device is measured to gather information about what it is doing.

The attached `.jls` file contains measurements of the current consumption of a real microcontroller board executing the supplied code.
It can be opened and viewed in the Joulescope application.

Analyse the provided firmware source code and the current measurements to extract the flag.



---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `misc`
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
