# Writeup: Gateway

| Property | Value |
| :--- | :--- |
| **Category** | `Blockchain` |
| **Points** | `188` |
| **Author** | `-` |
| **Solves** | `30` |

---

## 📝 Challenge Overview

The reboot has awakened an abandoned UPDC checkpoint guarding access to the Quantum Nexus Network. Its emergency gate still demands three proofs of clearance, but the officers who issued them vanished during The Severance. Find your way through all three doors and claim the credentials left inside.

The ticket is your team name, case-sensitive.

Flag Format : CSSCTF{CSS{...}} where CSS{...} is what you get from the netcat

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 34.116.80.78 31337`
- Category: `Blockchain`
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
