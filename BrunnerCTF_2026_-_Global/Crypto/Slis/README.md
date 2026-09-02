# Slis

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `100` |
| **Solves** | 382 |

## 📝 Description

**Difficulty:** Easy-Medium  
**Author:** Bond  

Brunnerne likes food 😋 and:

Some like it sHOrT 🍲

So we'll keep it short ☺️


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `crypto_slis.zip` | `platform_attachment` | ✅ Downloaded | [crypto_slis.zip](crypto_slis.zip) |

## 🚩 Flag & Solution

- [x] Solved

```
brunner{Pease_porridge_sHOrT_:)}
```

### Writeup / Notes

The challenge computes the sum of `lis = [n//(i+2) - n//(i+3) for i in range(9**5)]`.
This is a telescoping sum where intermediate floor division terms cancel out:
`sum(lis) = n//2 - n//(9**5 + 2) = n//2 - n//59051`.

Using binary search on `f(n) = n//2 - n//59051` to match `sum(lis) == 22263691028918788395010325066307464924652601045336492930678310479674861811846` recovers `n`.
Converting `n` to ASCII bytes yields: `brunner{Pease_porridge_sHOrT_:)}`.
