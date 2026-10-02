# Writeup: Insidotage

| Property | Value |
| :--- | :--- |
| **Category** | `Forensics` |
| **Points** | `500` |
| **Author** | `-` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

During a routine infrastructure audit, the security operations center detected abnormal resource spikes and suspicious outbound network traffic originating from an overlooked legacy server. 

Internal triage revealed that a rogue system administrator had abused their elevated privileges to repurpose the host for unauthorized computing, browser-based cryptocurrency operations, and illicit personal activities. Realizing an investigation was imminent, the insider attempted to cover their tracks by wiping key directories and purging activity logs before the server was isolated.

Despite their anti-forensic efforts, residual artifacts were preserved by the incident response team. Analyze the remaining evidence to reconstruct the rogue administrator's illicit deployment and uncover the personal digital footprint left behind.

Download [here](https://drive.google.com/file/d/1Zec3yurmPjqOy_0colfdLLKwx2zRp2ih/view?usp=sharing)

Connect: `nc 113.20.103.55 1336`

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
