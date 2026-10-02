# Writeup: Super Agent

| Property | Value |
| :--- | :--- |
| **Category** | `Misc` |
| **Points** | `500` |
| **Author** | `-` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

My friend Yobdas vibe-coded a Qwen-based CTF agent with a mode called super_mode, capable of solving any CTF challenge. It became so powerful that he decided not to let anyone use it.
Somehow, the trained super_mode were leaked and can now be used anywhere. Maybe he shouldn't have vibe-coded the web app either.

Target: Use the leaked super_mode to solve ctf_super_agent_can_solve_this.challage.

Download [here](https://drive.google.com/file/d/1T2IEDguI1WOQB9yWAZOu6j6R05d5d407/view?usp=sharing)

Connect: `https://web-chall-cscv.space/`

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
