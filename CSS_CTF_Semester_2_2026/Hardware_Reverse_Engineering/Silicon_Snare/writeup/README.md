# Writeup: Silicon Snare

| Property | Value |
| :--- | :--- |
| **Category** | `Hardware: Reverse Engineering` |
| **Points** | `250` |
| **Author** | `-` |
| **Solves** | `275` |

---

## 📝 Challenge Overview

The Kuiper Belt relay fail-safe is a hardwired optical routing matrix. 

Thanks to the bravery of a specific R2-series astromech droid, you have been provided the original schematic for its layout and proprietary analogue logic nodes. Trace the signal paths through the gates and find the one 32-bit input pattern that drives the centre node, Override, to logic high (1).
* Software won't help you much here. The only thing to follow is the wire.
* Some wires will intentionally overlap to hinder your efforts. Thankfully, you have its SVG; it will let you zoom in infinitely to inspect for detail. Push on!

Submit CSSCTF{…}. 
* Inside the braces, enter 32 bits (32 characters, 1s and 0s) with no spaces. I00, at 12 o’clock, is the first bit. Read clockwise through I31. 



This challenge is inspired by the same work bare-metal hardware engineers conduct when reverse engineering proprietary dies. Believe it or not, but this problem is trivial in comparison to their work; in real life, analysts must decap a proprietary chip, image the die, and trace the gates under microscope to see what routes where. Among other discoveries, this process may identify a backdoor.


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Hardware: Reverse Engineering`
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
