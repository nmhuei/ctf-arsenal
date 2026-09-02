# Writeup: Headache

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `69` |
| **Author** | `-` |
| **Solves** | `72` |

---

## 📝 Challenge Overview

<p><a href="/tasks/Headache_dd252a8948d2ec605553e4047246b8f81cf801cd.txz"><strong>Headache</strong></a>
is a haunted math blender. Crack its secret matrices, forge tags, get flag.</p>
<p><code>nc 65.109.208.91 1337</code></p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `nc 65.109.208.91 1337`
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

- Status: `- [x] Solved`
- Flag: `ASIS{c0uPleD_n0nL1n3Ar_Dynam!c5_R3c0vEry_v1A_p0l3s_&_l34st_squ4r3s!!}`
