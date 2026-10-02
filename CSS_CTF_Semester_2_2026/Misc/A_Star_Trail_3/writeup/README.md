# Writeup: A Star Trail 3

| Property | Value |
| :--- | :--- |
| **Category** | `Misc` |
| **Points** | `120` |
| **Author** | `-` |
| **Solves** | `186` |

---

## 📝 Challenge Overview

Polaris Logistics has seemingly had a database corruption in the star maps of Sector-A89J3. With routing and deliveries unable to be completed for the foreseeable future, *you*, cadet, have been tasked with fixing this problem. Otherwise, you can consider yourself **fired**. Thankfully, all of the planetary body entries are still there, only their paths to neighbouring bodies have been destroyed. We can't seem to remember what rule we used to generate our routes but you can presumably find patterns in your previous postal appointments. Once you've got those records restored, get a move on with the next delivery from `iJ2ZcO` to `pJk9vy` to prove it.

Report to command your flightpath by taking the first letter of the ID of your first stop (`iJ2ZcO`), the second letter of your second stop, the third letter of your third stop, and so on, wrapping back around to the first letter on your 7th, 13th, 19th, etc. stop. Your flightpath flag is case sensitive. For example: if your path from ASTART to ZFINAL was BCDEFG, hijklm, NOPQRS, tuvwxy, ZFINAL the flag would be `CSSCTF{ACjQxL}`. (The flag for this challenge may not be easily recognisable)

\- Polaris Logistics

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
