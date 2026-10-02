# Writeup: The Astrolobe Overwrite

| Property | Value |
| :--- | :--- |
| **Category** | `Misc` |
| **Points** | `711` |
| **Author** | `-` |
| **Solves** | `29` |

---

## 📝 Challenge Overview

When "The Severance" hit in 2100, the Kuiper Relay wasn't abandoned. Instead, it was locked into a loop governed by the Council. To prevent manual takeover, the council's instruction consumes and rewrites its own memory.

To force an administrative override, your payload must achieve harmonic resonance across the three rings of the Astrolabe:
1. Unravel the permutation field of the first gate.
2. Stabilize the coupled wave recurrence across the lattice.
3. Lock onto the projective coordinates of the orbital horizon.

The telemetry receiver requires exact synchronization with the beacon and will purge the core if total execution falls outside the quantum decay window.

Flag Format: CSSCTF{...}

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 34.116.80.78 7654`
- Category: `Misc`
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
