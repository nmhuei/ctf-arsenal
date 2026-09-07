# Writeup: fork

| Property | Value |
| :--- | :--- |
| **Category** | `blockchain` |
| **Points** | `500` |
| **Author** | `hoover` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

A small Starcoin network is running: one block producer and two validators, peered together
and agreeing with each other. The producer runs sequential execution, while the validators
run Block-STM configured with a concurrency level of 8.
For ordinary traffic nobody can tell the difference, right?

Your goal is to break consensus in the latest Starcoin nodes. From your one funded account, 
send a transaction that make the validators
permanently disagree with the producer and halt. The moment the network is forked, you will get the flag.

> [!NOTE]
> This is a 0day challenge and we are hoping you keep th{is|ese} 0day{|s} to yourself until the vulnerabilit{y|ies} {is|are} patched.

> [!WARNING]
> Do NOT attack any Starcoin mainnet node that may be running this configuration. NNS CTF and its organizers accept no liability or legal consequences

> [!IMPORTANT]
> The service may take some time to start. Please be patient.



---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `blockchain`
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
