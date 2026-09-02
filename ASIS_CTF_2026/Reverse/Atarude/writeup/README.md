# Writeup: Atarude

| Property | Value |
| :--- | :--- |
| **Category** | `Reverse` |
| **Points** | `450` |
| **Author** | `-` |
| **Solves** | `3` |

---

## 📝 Challenge Overview

<p>The binary is willing to talk, but only in hex and only on its own terms. It gives you a few local oracle lanes, then refuses to hand over the flag until you forge fresh ciphertexts for all of them.
Reverse the weird little <a href="/tasks/Atarude_e39d6ecbf3f6d04dee16fc4a9046770fa3bdd9f3.txz"><strong>Atarude</strong></a>, find the hidden relations, and convince flag.enc that you belong here.</p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Reverse`
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
