# Writeup: git gud

| Property | Value |
| :--- | :--- |
| **Category** | `boot2root` |
| **Points** | `500` |
| **Author** | `0xle` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

GitHub just lost another 9 from their uptime, I think it's time to move
to another platform. So, I decided to host my own Git instance.

> [!NOTE]
> The flag is located at `/flag.txt`.

> [!NOTE]
> This is a 0day challenge and we are hoping you keep th{is|ese} 0day{|s} to yourself until the vulnerabilit{y|ies} {is|are} patched.



---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `git-gud-a7294a1a23fb.chall.nnsc.tf:443`
- Category: `boot2root`
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
