# Writeup: Orthogonal Singularity

| Property | Value |
| :--- | :--- |
| **Category** | `Misc` |
| **Points** | `600` |
| **Author** | `-` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

Somewhere listening posts along the galactic rim have intercepted a telemetry beacon broadcasting near the event horizon.

To stabilize the link and extract the core telemetry, you must:
1. Pass the handshake gate before the uplink decays.
2. Track the carrier's 16 kHz trajectory through the noise and lock the frequency bounds.
3. Trace the topology of the underlying topological braid to collapse the singularity.

Flag Format: CSSCTF{...}

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 34.116.80.78 7878`
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

- Status: `- [ ] Solved`
- Flag: `FLAG{...}`
