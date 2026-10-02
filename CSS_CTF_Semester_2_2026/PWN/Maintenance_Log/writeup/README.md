# Writeup: Maintenance Log

| Property | Value |
| :--- | :--- |
| **Category** | `PWN` |
| **Points** | `50` |
| **Author** | `-` |
| **Solves** | `112` |

---

## 📝 Challenge Overview

Our diagnostics terminal logged an anomaly during maintenance. The vendor insists their service is fortified with stack canaries and safe from memory corruption, but the interface IS LEAKING.

Can you forge a maintenance report, bypass the perimeter, and acquire administrative clearance?

Flag Format: CSSCTF{...}

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 34.116.80.78 7312`
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

- Status: `- [ ] Solved`
- Flag: `FLAG{...}`
