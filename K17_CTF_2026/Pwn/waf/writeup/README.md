# Writeup: waf

| Property | Value |
| :--- | :--- |
| **Category** | `Pwn` |
| **Points** | `181` |
| **Author** | `-` |
| **Solves** | `48` |

---

## 📝 Challenge Overview

there's some holes in this WAF

Connection command: `nc chal.secso.cc 4006`

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `chal.secso.cc:4006`
- Category: `Pwn`
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
