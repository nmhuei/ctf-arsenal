# Writeup: BYOC

| Property | Value |
| :--- | :--- |
| **Category** | `pwn` |
| **Points** | `274` |
| **Author** | `hoover` |
| **Solves** | `13` |

---

## 📝 Challenge Overview

I got tired of hiding bugs for you to find, so I cut out the middleman

You have 200 bytes of memory that is readable, writable and executable at your disposal

Bring your own code.

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
