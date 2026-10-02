# Writeup: Dockside Ticket Office

| Property | Value |
| :--- | :--- |
| **Category** | `PWN` |
| **Points** | `25` |
| **Author** | `-` |
| **Solves** | `139` |

---

## 📝 Challenge Overview

The dockside ticket office manages temporary harbour access tickets.

You can create, cancel, edit, and use a ticket.

A cancelled ticket should no longer be usable, but this old terminal may not handle ticket memory safely.

Can you turn a cancelled ticket into emergency harbour access?

Flag Format: CSSCTF{}

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `PWN`
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

- Status: `- [x] Solved`
- Flag: `CSSCTF{us3_4ft3r_fr33_d0cks1d3}`
