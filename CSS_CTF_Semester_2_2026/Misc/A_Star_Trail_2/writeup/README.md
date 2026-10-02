# Writeup: A Star Trail 2

| Property | Value |
| :--- | :--- |
| **Category** | `Misc` |
| **Points** | `75` |
| **Author** | `-` |
| **Solves** | `336` |

---

## 📝 Challenge Overview

Congrats on your first, successful delivery cadet! Now that you've got a small taste of logistics and routing, take a gander at this larger galactic map. You've got quite a few more stops this time but thankfully, you won't have to be put to cryosleep now that you've gained your lightspeed vehicle licence. Today, your task is to make it from planetary body `S0jRxc` to planetary body `yRJyDb`. Chart out a path and **don't** be late; we expect you to make it there in a reasonable time. You'll have to do a bit of work to make sense of everything since our database is stored as Markdown files where each planet links to its neighbours with a wikilink but it should be easy work once you get used to it.

Report to command your flightpath by taking the first letter of the ID of your first stop (`S0jRxc`), the second letter of your second stop, the third letter of your third stop, and so on, wrapping back around to the first letter on your 7th, 13th, 19th, etc. stop. Your flightpath flag is case sensitive. For example: if your path from ASTART to ZFINAL was BCDEFG, hijklm, NOPQRS, tuvwxy, ZFINAL the flag would be `CSSCTF{ACjQxL}`

\- Polaris Logistics.

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
