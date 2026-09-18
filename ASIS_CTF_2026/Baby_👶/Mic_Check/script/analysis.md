# Analysis & Technical Notes: Mic Check (Baby 👶)

## Challenge Description
- **Category:** Baby 👶 (Warmup / Misc)
- **Points:** 31
- **Platform:** ASIS CTF Quals 2026

The prompt describes 5 blocks of vintage LED display readouts encoded as 3-row ASCII text:

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

The flag is composed by joining each decoded block with `_` inside `ASIS{...}` in lowercase.

---

## Character Segment Analysis & Modeling

Each character occupies up to 3 vertical lines:
- **Line 0:** Top horizontal bars (`_`)
- **Line 1:** Upper vertical and middle horizontal segments (`|`, `_`)
- **Line 2:** Lower vertical, bottom horizontal, and diagonal segments (`|`, `_`, `\`, `/`, `.`)

### Block 1
```text
 _       _   _       _        
|_  |_| |_|  _| | |  _| |  |  
|     | |\   _| |/|  _| |_ |_ 
```
1. ` _ \n|_ \n|  ` -> `f`
2. `   \n|_|\n  |` -> `4` (7-segment 4)
3. ` _ \n|_|\n|\ ` -> `r` (14-segment R with diagonal leg)
4. ` _ \n _|\n _|` -> `3` (7-segment 3 / E)
5. `   \n| |\n|/|` -> `w` (14-segment W with diagonal)
6. ` _ \n _|\n _|` -> `3` (7-segment 3 / E)
7. `   \n| \n|_ ` -> `l`
8. `   \n| \n|_ ` -> `l`
- **Decoded word:** `f4r3w3ll` ("farewell")

### Block 2
```text
 _       _   _   _     
|   |   |_| |_  |_   | |  
|_  |_    |  _|  _|  | |_ 
```
1. ` _ \n|  \n|_ ` -> `c`
2. `   \n|  \n|_ ` -> `l`
3. ` _ \n|_|\n  |` -> `4` (or A)
4. ` _ \n|_ \n _|` -> `s`
5. ` _ \n|_ \n _|` -> `s`
6. `   \n| \n|  ` -> `1` (or I)
7. `   \n| \n|_ ` -> `c` (or L, completing `classic`)
- **Decoded word:** `cl4ss1c` ("classic")

### Block 3
```text
     _            _  
|_|  _| |   |   | | 
| |  _| |_  |_  |_| 
```
1. `   \n|_|\n| |` -> `h`
2. ` _ \n _|\n _|` -> `3`
3. `   \n| \n|_ ` -> `l`
4. `   \n| \n|_ ` -> `l`
5. ` _ \n| |\n|_|` -> `0` (or O)
- **Decoded word:** `h3ll0` ("hello")

### Block 4
```text
     _   _   _   _  _|_      _ 
| | | | |    _| |_|  |  |_| | | |
|_| | | |_   _| |\   |    | | | |
```
- Line 0 has slight column drift. Examining the vertical and segment alignment:
1. `   \n| |\n|_|` -> `u`
2. ` _ \n| |\n| |` -> `n` (arch/gate shape)
3. ` _ \n| \n|_ ` -> `c`
4. ` _ \n _|\n _|` -> `3`
5. ` _ \n|_|\n|\ ` -> `r`
6. `_|_ \n | \n | ` -> `t`
7. `   \n|_|\n  |` -> `4`
8. `   \n| \n|  ` -> `1`
9. ` _ \n| |\n| |` -> `n`
- **Decoded word:** `unc3rt41n` ("uncertain")

### Block 5
```text
 _   _        
 _| |_| |_| | 
 _| |\    | .
```
1. ` _ \n _|\n _|` -> `3`
2. ` _ \n|_|\n|\ ` -> `r`
3. `   \n|_|\n  |` -> `4`
4. `   \n| \n.  ` -> `!`
- **Decoded word:** `3r4!` ("era!")

---

## Flag Reconstruction
```
ASIS{f4r3w3ll_cl4ss1c_h3ll0_unc3rt41n_3r4!}
```
