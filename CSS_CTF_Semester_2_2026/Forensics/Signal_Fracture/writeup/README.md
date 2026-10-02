# Writeup: Signal Fracture

| Property | Value |
| :--- | :--- |
| **Category** | `Forensics` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `308` |

---

## 📝 Challenge Overview

KBR-17 came back online for only fourteen seconds before the Nexus fabric collapsed again. A passive tap captured the relay's final uplink, and technicians recovered the relay drive exactly as it was after emergency shutdown.

Two details survived in the maintenance notes: the scheduler catalog was intact even though the spool index had been purged and uplink retries may have produced more than one copy of the same fragment.

Flag Format: CSSCTF{...}

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Forensics`
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
- Flag: `FLAG{...}`
