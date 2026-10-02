# Writeup: Res Impossibilis

| Property | Value |
| :--- | :--- |
| **Category** | `Forensics` |
| **Points** | `500` |
| **Author** | `-` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

During routine network monitoring, our Security Operations Center (SOC) detected suspicious behavioral anomalies originating from an internal enterprise Linux workstation.

Suspecting a security breach, the Incident Response team swiftly isolated the host and captured a full physical memory image of the active machine before taking it offline.

As the lead digital forensics investigator on this case, your mission is to reconstruct the attack and uncover the key artifacts left behind in memory.

Determine the answers to the following questions:

1. What is the email address of the account containing the malware?
2. What is the sha-256 hash of the initial malware binary responsible for collecting target files? (lowercase)
3. What is the password to unlock the exfiltrated documents archive?
4. What is the md5 hash string visible in the image captured by the surveillance agent? (lowercase)


Once you have identified all four answers, construct the final flag using the following format:

`cscv2026{answer1_answer2_answer3_answer4}`

Submit the flag with answers in the exact order shown above.

Download [here](https://drive.google.com/file/d/1Zm4qNm0U48djWZpezVvGaeiORhIWCd8M/view?usp=sharing)

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Forensics`
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
