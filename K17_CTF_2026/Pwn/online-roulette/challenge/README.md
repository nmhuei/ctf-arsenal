# online-roulette

| Property | Value |
| :--- | :--- |
| **Category** | `Pwn` |
| **Points** | `100` |
| **Solves** | 142 |
| **Tags** | `beginner`, `pwn`, `beginner` |

## 🔌 Connection / Service
```bash
chal.secso.cc:4000
```

- URL: [https://man7.org/linux/man-pages/man2/ptrace.2.html)](https://man7.org/linux/man-pages/man2/ptrace.2.html))

```bash
nc chal.secso.cc 4000
```

## 📝 Description

live roulette players keep complaining that they dont get enough spins per hour, so we are introducing ROULETTE ONLINE!!! despite the (small) house edge, this minibolt guy keeps winning???

Note: We've added a debugging tool on the remote to help you out a bit.
The `SNAPSHOT()` call will [magically](https://man7.org/linux/man-pages/man2/ptrace.2.html) print out a view of the program stack.
You can ignore the snapshot stuff in the code, it's just there to enable this functionality.


Connection command: `nc chal.secso.cc 4000`


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `chal.c` | `platform_attachment` | ✅ Downloaded | [chal.c](chal.c) |

### 🔗 External Links in Description

- [magically](https://man7.org/linux/man-pages/man2/ptrace.2.html) (`generic_url`)

## 🚩 Flag & Solution

- [ ] Solved

```
FLAG{...}
```

### Writeup / Notes

*(Write your solution steps and notes here)*
