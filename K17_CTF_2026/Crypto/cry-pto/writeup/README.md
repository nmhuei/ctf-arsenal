# Writeup: cry-pto

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `236` |

---

## 📝 Challenge Overview

a lot of ppl cry when they see crypto...but you...you get back up every time you are knocked down


Connection command: `nc chal.secso.cc 2000`

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `chal.secso.cc:2000`
- Category: `Crypto`
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
- Flag: `K17{y0u_ar3_f1ll3d_w1th_deter1min4t10n}`
