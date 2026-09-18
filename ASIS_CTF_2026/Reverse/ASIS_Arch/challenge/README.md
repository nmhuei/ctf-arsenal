# ASIS Arch

| Property | Value |
| :--- | :--- |
| **Category** | `Reverse` |
| **Points** | `34` |
| **Solves** | 203 |
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

- [x] Solved

```
ASIS{M1ddL3_3nd14n_N1bbL35_M4k3_Q3MU_D122y!}
```

### Writeup / Notes

The challenge involves reversing a custom 16-bit RISC architecture (`ASISARCH`) implemented in `qemu-asisarch`. The binary decrypts and executes instructions with a position-dependent instruction permutation. The verification consists of 10 rounds of a 3-layer cipher (S-box + key mixing, modular addition diffusion, cellular rotation diffusion) over 22 16-bit words (44 bytes). Each layer was inverted to recover the flag.

See [`../writeup/README.md`](../writeup/README.md) for full writeup and [`../solver/solve.py`](../solver/solve.py) for the exploit script.

