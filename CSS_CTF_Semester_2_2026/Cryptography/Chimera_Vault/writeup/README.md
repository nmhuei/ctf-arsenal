# Writeup: Chimera Vault

| Property | Value |
| :--- | :--- |
| **Category** | `Cryptography` |
| **Points** | `136` |
| **Author** | `-` |
| **Solves** | `70` |

---

## 📝 Challenge Overview

The ancient custodians of the Chimera Vault didn't rely on standard asymmetric primitives to secure their root register.

Demodulate the carrier, trace the invariant through the matrix state transitions, and invert the resonance to breach the vault.

Flag Format: CSSCTF{...}

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 34.116.80.78 7334`
- Category: `Cryptography`
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
