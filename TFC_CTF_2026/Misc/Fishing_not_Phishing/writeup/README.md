# Writeup: Fishing not Phishing

| Property | Value |
| :--- | :--- |
| **Category** | `Misc` |
| **Points** | `382` |
| **Author** | `Walker` |
| **Solves** | `18` |

---

## 📝 Challenge Overview

Not every vessel leaves a clear trail behind.  
<br><br>

Three years ago, during this same month, one vessel departed from port and eventually began fishing somewhere offshore. The information needed to reconstruct that moment is still out there...  
<br><br>

Find the following:
<br>

 - the vessel's MMSI
<br>

 - the port of departure
<br>

 - the date when the vessel started fishing
<br>

 - the time when the fishing activity started
<br>

 - the distance, in kilometers, between the departure port and the location where fishing began
<br>


<br>
Flag Format


<br>
TFCCTF{MMSI_Port Name_DD.MM.YYYY_HH:MM_AM/PM_distance}



The time must be provided in UTC, using the 12-hour format with AM or PM.  


The distance must be expressed in kilometers, rounded to one decimal place.


Port Name is in lowercase


Example flag
TFCCTF{247363350_bari_07.09.2028_09:45_PM_130.7}

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Misc`
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
