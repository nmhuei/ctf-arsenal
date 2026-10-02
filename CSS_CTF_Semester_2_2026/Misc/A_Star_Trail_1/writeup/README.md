# Writeup: A Star Trail 1

| Property | Value |
| :--- | :--- |
| **Category** | `Misc` |
| **Points** | `20` |
| **Author** | `-` |
| **Solves** | `331` |

---

## 📝 Challenge Overview

(You may have seen this last year)

Polaris Logistics has an urgent delivery that needs to be transported across the star system. As the pilot of this V.I.P. (Very Important Package), you need to begin planning your trip from *Earth* to *Lancer-RXKRD* immediately. Remember to follow company protocol; you *have* to follow the designated paths between planet/oids to comply with interplanetary law. If you can’t deliver the V.I.P. in under 25 days, you might as well forget about your end of year bonus.

\- Polaris Logistics.

Submit your flag using the by combining the first character of each planet/oid in your path together and then adding the number of days your path takes (with 1 decimal place) onto the end, separated by a dash. E.g. if your path from A-PLANET TO B-PLANET was PAPA, OSCAR, SIERRA, TANGO, 2025PLANET and took exactly 5 days, the flag would be `CSSCTF{POST2-5.0}`

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Misc`
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
