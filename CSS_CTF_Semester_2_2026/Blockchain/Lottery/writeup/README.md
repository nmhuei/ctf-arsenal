# Writeup: Lottery

| Property | Value |
| :--- | :--- |
| **Category** | `Blockchain` |
| **Points** | `292` |
| **Author** | `-` |
| **Solves** | `21` |

---

## 📝 Challenge Overview

Beyond the checkpoint, a Beltway Bandits gambling terminal has resumed broadcasting: “Ten wins in a row. One fortune. No second chances.” Once used to distribute stolen credits, it now holds an access key to the Bandits’ hidden network. Beat the house and claim it before they return to collect.

The ticket is your team name, case-sensitive

Flag Format : CSSCTF{CSS{...}} where CSS{...} is what you get from the netcat

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 34.116.80.78 31338`
- Category: `Blockchain`
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
