# Writeup: Echoes of the Relay

| Property | Value |
| :--- | :--- |
| **Category** | `Forensics` |
| **Points** | `33` |
| **Author** | `-` |
| **Solves** | `136` |

---

## 📝 Challenge Overview

Echoes of the Relay

The Kuiper Belt Relay was one of the first Nexus nodes to come back online after the Severance.

Its recovery lasted exactly 47 seconds.

Then it went silent again.

Before the node disappeared, an automated recovery system transmitted a damaged storage image from one of its maintenance terminals.

Nexus engineers inspected the visible files but found nothing useful.

However, the terminal's final operator apparently tried to preserve something before the system shut down.

Recover the operator's final transmission.

Provided file: relay_backup.img
Flag format: CSSCTF{...}

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
