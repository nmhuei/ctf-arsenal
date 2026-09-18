# Writeup: Echoes

| Property | Value |
| :--- | :--- |
| **Category** | `Hardware` |
| **Points** | `500` |
| **Author** | `-` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

<p>Two <a href="/tasks/Echoes_a6abb166d71df1315e611540520dde97d6811a75.txz"><strong>chips</strong></a> tried to talk at once. Now their argument is your problem.</p>
<p><strong>Hint:</strong> Echoes do not speak one segment at a time.</p>
<p>The three PRBS reference intervals reveal a five-step history in the analog signal. Use this learned model to decode the two unknown intervals as a path through four states:</p>
<p><code>NONE, A, B, and AB</code></p>
<p>When you have stream candidates, bind them with:</p>
<p>stream_a + stream_b + public_nonce</p>
<p>Then verify the HMAC tag stored in <code>eeprom.bin</code>.</p>
<p>All required files are already provided: <code>session.ecap</code>, <code>transaction.json</code>, and <code>eeprom.bin</code>.</p>


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Hardware`
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
