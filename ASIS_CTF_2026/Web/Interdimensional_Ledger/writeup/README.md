# Writeup: Interdimensional Ledger

| Property | Value |
| :--- | :--- |
| **Category** | `Web` |
| **Points** | `90` |
| **Author** | `-` |
| **Solves** | `52` |

---

## 📝 Challenge Overview

<p>Keeping track of portal fluid, Meeseeks invoices, and unpaid Galactic Federation taxes is difficult, even for the smartest man in the universe. So Rick is working on an interdimensional spreadsheet to handle the calculations automatically.</p>
<p>As usual, he insists the system is perfectly secure and that any strange calculations are simply “features of interdimensional accounting.”</p>
<p><code>http://91.107.252.227:3000‍</code></p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `http://91.107.252.227:3000`
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
