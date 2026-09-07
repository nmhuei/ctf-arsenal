# Time Lock

| Property | Value |
| :--- | :--- |
| **Category** | `rev` |
| **Points** | `363` |
| **Author** | hoover |
| **Solves** | 7 |

## 📝 Description

New to reverse engineering? This beginner challenge is an introduction to
replacing the library functions a Linux program calls, so it sees what you
want it to see.

The provided `x86-64` ELF is a sealed archive. It asks the C standard
library what day it is, refuses to open unless the answer is
1 January 9999, and prints `sealed` every other day of the year. Waiting
is not an option, and neither is changing your system clock.

The dynamic loader lets you put your own shared library in front of libc,
so the program ends up calling your function instead of the real one.
Write a replacement for the call it uses to read the clock, preload it,
and run the program again. Note that patching the date check on its own
will not be enough. The key is derived from the answer the program gets
back, not merely compared against it.


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `rev_time-lock.tar.gz` | `platform_attachment` | ✅ Downloaded | [rev_time-lock.tar.gz](rev_time-lock.tar.gz) |

## 🚩 Flag & Solution

- [ ] Solved

```
FLAG{...}
```

### Writeup / Notes

*(Write your solution steps and notes here)*
