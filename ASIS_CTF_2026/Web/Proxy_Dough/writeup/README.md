# Writeup: Proxy Dough

| Property | Value |
| :--- | :--- |
| **Category** | `Web` |
| **Points** | `62` |
| **Author** | `-` |
| **Solves** | `82` |

---

## 📝 Challenge Overview

<p>We want the secret recipe of this famous cookie dough, can you get it ?</p>
<p>PS: The <a href="/tasks/ProxyDough_faab7cb2ef78e1be178d2feffc266a4e6fba3233.txz"><strong>source code</strong></a> is given for information, however, we recommend solving the challenge on the remote instance. Bruteforce is not allowed, the source code on the remote instance is the same has given.</p>
<p>URL: <code>https://proxydough.net</code></p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `https://proxydough.net`
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
