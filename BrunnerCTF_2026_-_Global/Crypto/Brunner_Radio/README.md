# Brunner Radio

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `100` |
| **Solves** | 341 |

## 📝 Description

**Difficulty:** Medium  
**Author:** Bond  

To readily be able to share our delicious news with brunsviger-fans even in situations when there is no internet connection available 🚫 we at Brunnerne Inc. are also working on a radio-broadcasting scheme 📡

... But I forget: Which frequency were we transmitting on? 📻


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `crypto_brunner-radio.zip` | `platform_attachment` | ✅ Downloaded | [crypto_brunner-radio.zip](crypto_brunner-radio.zip) |

## 🚩 Flag & Solution

- [x] Solved

```
brunner{Brunsviger_is_in_the_air_<3}
```

### Writeup / Notes

Reconstructed 9 broadcast channels from the sequential aggregate matrix using Gaussian elimination over the divisor matrix. Stream 8 contains the real flag.
