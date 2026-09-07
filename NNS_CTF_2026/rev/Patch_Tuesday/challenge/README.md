# Patch Tuesday

| Property | Value |
| :--- | :--- |
| **Category** | `rev` |
| **Points** | `383` |
| **Author** | hoover |
| **Solves** | 6 |

## 📝 Description

New to reverse engineering? This beginner challenge is an introduction to
dynamic debugging and patching Windows programs.

The provided `x86-64` `.exe` promises a free flag, but it does not behave the
way we want. Open it in a debugger such as x64dbg or IDA Free, run it, and
step through the code that decides whether you receive the flag. Watch how
the program compares values and follows a conditional jump.

Try changing that jump while debugging, or patch the instruction in the
executable and run your modified file again. Your goal is to make the
program follow the path that produces the expected behavior.


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `rev_patch-tuesday.tar.gz` | `platform_attachment` | ✅ Downloaded | [rev_patch-tuesday.tar.gz](rev_patch-tuesday.tar.gz) |

## 🚩 Flag & Solution

- [ ] Solved

```
FLAG{...}
```

### Writeup / Notes

*(Write your solution steps and notes here)*
