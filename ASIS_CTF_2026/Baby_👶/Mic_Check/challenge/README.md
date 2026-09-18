# Mic Check

| Property | Value |
| :--- | :--- |
| **Category** | `Baby 👶` |
| **Points** | `31` |
| **Solves** | 252 |
| **Tags** | `Baby 👶` |

## 📝 Description

The analog signals have died out.
Only kind human eyes can still decode the vintage LED displays before the machines take over.

Read the following digital readouts below. Join the blocks with `_` inside `ASIS{...}` (all lowercase):

```
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


## 📦 Files & Resources

*No file attachments associated with this challenge.*

## 🚩 Flag & Solution

- [x] Solved

```
ASIS{f4r3w3ll_cl4ss1c_h3ll0_unc3rt41n_3r4!}
```

### Writeup / Notes

The challenge presents five vintage 7-segment / 14-segment LED display readouts encoded in 3-row ASCII art.
Decoding each block yields leetspeak words:
- Block 1: `f4r3w3ll` ("farewell")
- Block 2: `cl4ss1c` ("classic")
- Block 3: `h3ll0` ("hello")
- Block 4: `unc3rt41n` ("uncertain" - accounting for the drifted top row spacing)
- Block 5: `3r4!` ("era!")

Joining the blocks with `_` inside `ASIS{...}` gives `ASIS{f4r3w3ll_cl4ss1c_h3ll0_unc3rt41n_3r4!}`.
