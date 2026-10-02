# Writeup: Message System

| Property | Value |
| :--- | :--- |
| **Category** | `Pwn` |
| **Points** | `500` |
| **Author** | `-` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

We built a blazing-fast, lightweight internal messaging service to keep inter-process communications safe and reliable. Our developers were strictly told that memory safety is a state of mind.

Before you can access the system, you must first verify that you are not a robot. Once you're in, check the binary for vulnerabilities.

Download [here](https://drive.google.com/file/d/1n4wkxyoCaRhL5qz1h_heYmhkyT1J98Js/view?usp=sharing)

Connect: `nc 113.20.103.216 1337`


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
