# Writeup: rainier

| Property | Value |
| :--- | :--- |
| **Category** | `Osint` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `236` |

---

## 📝 Challenge Overview

Can you find where I took this photo? (I got drenched btw)

Enter the names of the roads at this intersection, in the format `K17{street1,street2}`, without the street type suffixes.

For example, if you think the roads are `Wallaby Way` and `George Street`, you could enter `K17{Wallaby,George}` or `K17{George,Wallaby}`.
Capitalisation will be ignored.


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Osint`
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
