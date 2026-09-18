# Hackel

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `24` |
| **Solves** | 525 |
| **Tags** | `Crypto`, `Baby 👶` |

## 🔌 Connection / Service
```bash
nc 65.109.208.91 3771
```

```bash
nc 65.109.208.91 3771
```

```bash
nc 65.109.208.91 3771
```

## 📝 Description

🗝️ Hackel

Our lead cryptographer [hackel](/tasks/Hackel_167b289c63c46836d376945105d757028321303a.txz) proudly announced a "revolutionary post-quantum vault" guarded by intricate algebraic group presentations.

With a search space boasting over **1.6 quadrillion** states, they confidently declared:

*"No supercomputer on Earth could brute-force our permutations before the heat death of the universe!"*

Well... brute force is for amateurs. Armed with a fresh cup of coffee, a notebook, and a touch of modern group theory, can you reconstruct the secret representation, unlock the vault, and claim the flag?

```
nc 65.109.208.91 3771
```


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `Hackel_167b289c63c46836d376945105d757028321303a.txz` | `platform_attachment` | ✅ Downloaded | [Hackel_167b289c63c46836d376945105d757028321303a.txz](Hackel_167b289c63c46836d376945105d757028321303a.txz) |

## 🚩 Flag & Solution

- [x] Solved

### Writeup / Notes

The challenge features an alleged post-quantum vault based on permutation group presentations. In reality, words representing 0 and 1 bits are formed from raw generator sequences without reduction modulo relations (`0` bits contain only `'a'`, while `1` bits contain `'b'`). Option 5 can be answered instantly in under 5 seconds by checking `'b' in word`, which immediately reveals the flag. Option 2 can also be decrypted offline with the same logic. Full details in [Writeup](file:///home/light/Workspace/CTF/ASIS_CTF_2026/Crypto/Hackel/writeup/README.md).

