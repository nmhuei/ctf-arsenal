# Writeup: Count on me!

| Property | Value |
| :--- | :--- |
| **Category** | `boot2root` |
| **Points** | `500` |
| **Author** | `0xle` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

You can always count on me! Or..?

> [!NOTE]
> The flag is located at `/root/flag.txt`

> [!NOTE]
> This is a 0day challenge and we are hoping you keep th{is|ese} 0day{|s} to yourself until the vulnerabilit{y|ies} {is|are} patched.



---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `count-on-me-79a5d915b257.chall.nnsc.tf:443`
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
