# Writeup: MARIONETTE

| Property | Value |
| :--- | :--- |
| **Category** | `Pwn` |
| **Points** | `500` |
| **Author** | `-` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

The Puppeteer's Grand Theatre presents tonight: a one-act play performed
entirely by marionettes. The PuppetScript VM interprets your commands and
brings the puppets to life on stage.

But rumours say the backstage rigging has a loose screw. One wrong pull
and the puppets might dance to YOUR tune instead of the Puppeteer's...

Can you take control of the theatre and steal the Puppeteer's secret script?

Download [here](https://drive.google.com/file/d/1NqBFhA_iwY-aaw666e1OCMeQF0OlHg6T/view?usp=sharing)

Connect: `nc 113.20.103.216 9999`

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Pwn`
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
