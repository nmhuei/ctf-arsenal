# Writeup: LeakMeAk

| Property | Value |
| :--- | :--- |
| **Category** | `Reverse` |
| **Points** | `39` |
| **Author** | `-` |
| **Solves** | `165` |

---

## 📝 Challenge Overview

<p>In <a href="/tasks/LeakMeAk_f9e29089aee4968435d8e68e316f36d37d1bd002.txz"><strong>LeakMeAk</strong></a>, even the flag has trust issues.</p>
<p><code>nc 65.109.208.91 3117</code></p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 65.109.208.91 3117`
- Category: `Reverse`
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
