# Writeup: Less is more

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `500` |
| **Author** | `-` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

<h1>Less is more</h1>
<p>We captured traffic from a prototype signing device. The implementation is small, but some records in the capture do not match a normal run. Note the <a href="/tasks/less_is_more_c21e39cc296efe86ee76902cae855a705bd74214.txz"><strong>less is more</strong></a>.</p>
<p>The device sealed its backup vault with a key derived from its secret matrices. Recover the vault key, open the vault, and take the <code>flag</code>.</p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Crypto`
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
