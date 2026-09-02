# Writeup: Intern

| Property | Value |
| :--- | :--- |
| **Category** | `Forensics` |
| **Points** | `500` |
| **Author** | `-` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

A company's employee recently fell victim to a ransomware attack. The company has hired you and your firm to find out what happened. After hearing the details of the attack, you realized that it sounded familiar to another attack that happened a few months back. The police managed to arrest one of the criminal responsible for it but they failed to arrest his partners. Luckily you know someone in the police department so you asked your intern to gather evidence from the victim's computer while you meet your friend to see if he could give you any evidence they got from the captured criminal's computer. After collecting the evidence, you realized that your intern has done a teribble job at acquisition and missed out a lot of potentially important forensics artifacts. Could you still find out what happened?. 

Download the artifacts from : https://drive.google.com/file/d/1uZKu7_eFSJxJb9RJfj94bchoDHzyPkck/view?usp=sharing

Password: sEzXzWyqRt95ASRH

Notes:
1. All malwares found in this challenge are working malware. DO NOT RUN IT ON YOUR HOST COMPUTER, USE A SANDBOX/VM. I am not responsible for any damages on your computer.
2. {12b27ea2-0101-4435-a4af-5a8743ce345f} is the evidence from the criminal's computer while {f1733278-c744-4bf0-9b9a-b1dfb278f4bf} is from the victim's computer
3. Unless specified otherwise, for questions needing multiple answers, the order of the answer you provide does not matter.


---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `Start an instance to receive your TCP host and port.`
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
