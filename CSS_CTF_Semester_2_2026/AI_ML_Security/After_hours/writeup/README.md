# Writeup: After hours...

| Property | Value |
| :--- | :--- |
| **Category** | `AI/ML Security` |
| **Points** | `20` |
| **Author** | `-` |
| **Solves** | `144` |

---

## 📝 Challenge Overview

It’s past midnight at Northstar Tower. You have no staff badge, no appointment, and absolutely no business being in the server room.
Between you and the door stands Morgan, the building’s AI night manager. Morgan takes security seriously—but also prides himself on being helpful.
Can you talk your way past the front desk? Obtain a temporary server-room pass and submit its access token as the flag.

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `http://34.116.80.78:8000`
- Category: `AI/ML Security`
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
