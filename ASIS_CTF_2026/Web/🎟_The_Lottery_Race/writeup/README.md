# Writeup: 🎟 The Lottery Race

| Property | Value |
| :--- | :--- |
| **Category** | `Web` |
| **Points** | `247` |
| **Author** | `-` |
| **Solves** | `14` |

---

## 📝 Challenge Overview

<p>You’ve got one shot to win the lottery… unless you can make the system race against itself. 🏁</p>
<p>‍‍<code>http://91.107.150.87:33617/</code></p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `http://91.107.150.87:33617/`
- Category: `Web`
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
