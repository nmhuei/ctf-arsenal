# Writeup: mining-away

| Property | Value |
| :--- | :--- |
| **Category** | `misc` |
| **Points** | `500` |
| **Author** | `0xle` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

Minin' away
I don't know what to mine
I'll mine this anyway

Connect using:
```
socat TCP-LISTEN:25565,reuseaddr,fork OPENSSL:<instance>:1337
```



---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `misc`
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
