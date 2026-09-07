# No Strings Attached

| Property | Value |
| :--- | :--- |
| **Category** | `rev` |
| **Points** | `286` |
| **Author** | hoover |
| **Solves** | 12 |

## 📝 Description

New to reverse engineering? This beginner challenge is an introduction to
tracing the library calls a Linux program makes.

The provided `x86-64` ELF asks you to guess a passphrase. The passphrase
is the flag, but it is not written down anywhere in the file. Running
`strings` on the binary only gets you `guess:`, `correct` and `rejected`.
The program builds the real passphrase in memory first, and only then
hands it to a function in the C standard library to compare against yours.

Run the program under a library call tracer such as `ltrace` and watch the
comparison. Your goal is to read the passphrase out of the arguments the
program passes to it.


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `rev_no-strings-attached.tar.gz` | `platform_attachment` | ✅ Downloaded | [rev_no-strings-attached.tar.gz](rev_no-strings-attached.tar.gz) |

## 🚩 Flag & Solution

- [ ] Solved

```
FLAG{...}
```

### Writeup / Notes

*(Write your solution steps and notes here)*
