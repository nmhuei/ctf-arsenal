# Writeup: Mic Check

| Property | Value |
| :--- | :--- |
| **Category** | `Baby 👶` |
| **Points** | `31` |
| **Author** | `-` |
| **Solves** | `252` |

---

## 📝 Challenge Overview

The challenge presents five vintage LED display readouts rendered in 3-row ASCII art:

```text
[1]  _       _   _       _        
    |_  |_| |_|  _| | |  _| |  |  
    |     | |\   _| |/|  _| |_ |_ 

[2]  _       _   _   _     
    |   |   |_| |_  |_   | |  
    |_  |_    |  _|  _|  | |_ 

[3]      _            _  
    |_|  _| |   |   | | 
    | |  _| |_  |_  |_| 

[4]      _   _   _   _  _|_      _ 
    | | | | |    _| |_|  |  |_| | | |
    |_| | | |_   _| |\   |    | | | |

[5]  _   _        
     _| |_| |_| | 
     _| |\    | .
```

The objective is to decode the readouts into words, format them as lowercase leetspeak, and join them with underscores (`_`) inside `ASIS{...}`.

---

## 🔍 Analysis & Decoding

The characters are rendered in a vintage 7-segment / 14-segment alphanumeric LED font across 3 vertical text rows:
- Row 0: Top segment(s)
- Row 1: Upper-left, middle, and upper-right segments
- Row 2: Lower-left, bottom, and lower-right segments (plus diagonal segments such as `\` in `R` and `/` in `W`)

### Block 1
```text
 _       _   _       _        
|_  |_| |_|  _| | |  _| |  |  
|     | |\   _| |/|  _| |_ |_ 
```
- Char 1: ` _ \n|_ \n|  ` → `f`
- Char 2: `   \n|_|\n  |` → `4`
- Char 3: ` _ \n|_|\n|\ ` → `r`
- Char 4: ` _ \n _|\n _|` → `3`
- Char 5: `   \n| |\n|/|` → `w`
- Char 6: ` _ \n _|\n _|` → `3`
- Char 7: `   \n| \n|_ ` → `l`
- Char 8: `   \n| \n|_ ` → `l`
- **Result:** `f4r3w3ll` ("farewell")

### Block 2
```text
 _       _   _   _     
|   |   |_| |_  |_   | |  
|_  |_    |  _|  _|  | |_ 
```
- Char 1: ` _ \n|  \n|_ ` → `c`
- Char 2: `   \n|  \n|_ ` → `l`
- Char 3: ` _ \n|_|\n  |` → `4`
- Char 4: ` _ \n|_ \n _|` → `s`
- Char 5: ` _ \n|_ \n _|` → `s`
- Char 6: `   \n| \n|  ` → `1`
- Char 7: `   \n| \n|_ ` → `c` (or `l`) → fits `classic`
- **Result:** `cl4ss1c` ("classic")

### Block 3
```text
     _            _  
|_|  _| |   |   | | 
| |  _| |_  |_  |_| 
```
- Char 1: `   \n|_|\n| |` → `h`
- Char 2: ` _ \n _|\n _|` → `3`
- Char 3: `   \n| \n|_ ` → `l`
- Char 4: `   \n| \n|_ ` → `l`
- Char 5: ` _ \n| |\n|_|` → `0`
- **Result:** `h3ll0` ("hello")

### Block 4
```text
     _   _   _   _  _|_      _ 
| | | | |    _| |_|  |  |_| | | |
|_| | | |_   _| |\   |    | | | |
```
Note on Block 4: The top row has slight column drift relative to the lower rows. Analyzing the vertical segments:
- Char 1: `   \n| |\n|_|` → `u`
- Char 2: ` _ \n| |\n| |` → `n`
- Char 3: ` _ \n| \n|_ ` → `c`
- Char 4: ` _ \n _|\n _|` → `3`
- Char 5: ` _ \n|_|\n|\ ` → `r`
- Char 6: `_|_ \n | \n | ` → `t`
- Char 7: `   \n|_|\n  |` → `4`
- Char 8: `   \n| \n|  ` → `1`
- Char 9: ` _ \n| |\n| |` → `n`
- **Result:** `unc3rt41n` ("uncertain")

### Block 5
```text
 _   _        
 _| |_| |_| | 
 _| |\    | .
```
- Char 1: ` _ \n _|\n _|` → `3`
- Char 2: ` _ \n|_|\n|\ ` → `r`
- Char 3: `   \n|_|\n  |` → `4`
- Char 4: `   \n| \n.  ` → `!`
- **Result:** `3r4!` ("era!")

---

## 💻 Exploitation Strategy & PoC

A self-contained solver script is provided in [`../solver/solve.py`](../solver/solve.py):

```bash
python3 ../solver/solve.py
```

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `ASIS{f4r3w3ll_cl4ss1c_h3ll0_unc3rt41n_3r4!}`
