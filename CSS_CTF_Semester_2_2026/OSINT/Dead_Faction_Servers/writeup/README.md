# Writeup: Dead Faction Servers

| Property | Value |
| :--- | :--- |
| **Category** | `OSINT` |
| **Points** | `10` |
| **Author** | `-` |
| **Solves** | `122` |

---

## 📝 Challenge Overview

The old faction that ran Sector 9 didn't leave one trail — they
left several, and most of them are decoys. Whoever built this
infrastructure knew someone would come looking eventually, and
buried the real access key across two separate locations, split
in half, one piece scrambled beyond plain sight.

Your recon has already surfaced their handle and at least one
archived project. Don't trust the first thing you find — Sector
9's engineers were paranoid, and paranoid engineers plant false
leads.

Starting trace: bobdev508
Flag Format: CSSCTF{...}

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `OSINT`
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
