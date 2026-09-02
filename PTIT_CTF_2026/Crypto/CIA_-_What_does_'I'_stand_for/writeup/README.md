# Writeup: CIA - What does 'I' stand for?

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `39` |

---

## 📝 Challenge Overview

In an old intelligence archive, every message was accepted only after its source could be proven. Some agents trusted the seal, some trusted the courier, but the careful ones walked the route from the last mark back to the first before trusting the identity behind the message.

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `144.79.188.39:43975`
- Category: `Crypto`
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
