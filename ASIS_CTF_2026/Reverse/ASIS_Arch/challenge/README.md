# ASIS Arch

| Property | Value |
| :--- | :--- |
| **Category** | `Reverse` |
| **Points** | `64` |
| **Solves** | 80 |
| **Tags** | `Reverse` |

## 📝 Description

ASISARCH

We recovered a custom CPU emulator binary and a secure ROM image.
The architecture does not appear in any public manual. Recover the ISA, reverse the verification logic, and find the correct flag from new [ASIS Arch](/tasks/ASIS-Arch_2671a9f8046f73ecbbaa579a1daca1819e975772.txz).

Run it as:

```
chmod +x qemu-asisarch
./qemu-asisarch -M asisboard -kernel challenge.rom -nographic
```

Flag format: `ASIS{...}`


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `ASIS-Arch_2671a9f8046f73ecbbaa579a1daca1819e975772.txz` | `platform_attachment` | ✅ Downloaded | [ASIS-Arch_2671a9f8046f73ecbbaa579a1daca1819e975772.txz](ASIS-Arch_2671a9f8046f73ecbbaa579a1daca1819e975772.txz) |

## 🚩 Flag & Solution

- [ ] Solved

```
FLAG{...}
```

### Writeup / Notes

*(Write your solution steps and notes here)*
