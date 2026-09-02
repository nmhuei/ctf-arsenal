# Writeup: ASIS Arch

| Property | Value |
| :--- | :--- |
| **Category** | `Reverse` |
| **Points** | `64` |
| **Author** | `-` |
| **Solves** | `80` |

---

## 📝 Challenge Overview

We recovered a custom CPU emulator binary `qemu-asisarch` and a secure ROM image `challenge.rom`.
The architecture does not appear in any public manual. We need to reverse-engineer the custom VM instruction set architecture (ISA), instruction decoding logic, and ROM validation algorithm to recover the correct flag.

---

## 🔍 Reverse Engineering & Architecture Analysis

### 1. VM State Layout
The emulator allocates a VM structure pointer in `RBX`:
- `RBX + 0x0000 .. 0xffff`: 64 KB RAM / Memory address space.
- `RBX + 0x10000 .. 0x1000f`: Eight 16-bit general-purpose registers `R0` through `R7`.
- `RBX + 0x10010`: Stack Pointer (`SP`).
- `RBX + 0x10012`: Program Counter (`PC`).

### 2. Instruction Fetch & Decoding Scheme
Each instruction is 4 bytes long at address `PC = si`. The bytecode is scrambled using non-linear arithmetic and a permutation table:
- State constant:
  $$\text{ax} = ((\text{si} \oplus 0x9e37) \times 0x1039 + 0x79b9) \bmod 2^{16}$$
  $$\text{edi} = \text{rol16}(\text{ax}, 5)$$
  $$\text{idx} = (\text{ax} \gg 14) \ \& \ 3$$
- Permutation table at `.rodata:0x2140`:
  $$P = [[0, 1, 2, 3], [2, 0, 3, 1], [3, 2, 1, 0], [1, 3, 0, 2]]$$
- Opcode unscrambling:
  $$\text{opcode} = \text{rol8}\Big(\big((0x5d \times \text{si}) \oplus \text{edi} \oplus \text{mem}[\text{si} + P[\text{idx}][2]]\big) \ \& \ 0xff, \ (\text{edi} \gg 5) \ \& \ 0x1f\Big) \oplus 0x6d$$
- Register destination (`Rd`) and operand (`edx` / `Rs` / `imm`):
  $$Rd = \Big(\big(((\text{si} \times 7) \oplus (\text{edi} \gg 2) \oplus \text{rol8}(\text{mem}[\text{si} + P[\text{idx}][1]] \oplus \text{edi}, 4) \oplus \text{mem}[\text{si} + P[\text{idx}][0]]) \bmod 256 \times 5) \oplus 3\big) \ \& \ 7$$
  $$edx = \text{rol16}\Big(\big(\text{rol8}(\text{mem}[\text{si} + P[\text{idx}][3]] \oplus (\text{edi} \gg 8), 4) \ll 8\big) \ | \ \text{rol8}(\text{mem}[\text{si} + P[\text{idx}][1]] \oplus \text{edi}, 4), \ 5\Big)$$

### 3. Opcode Handlers
The dispatch jump table at `.data.rel.ro:0x35e0` contains handlers for:
- `MOV_IMM Rd, imm` (`0x1b00`)
- `ADD_IMM Rd, imm` (`0x1ad0`)
- `SUB_IMM Rd, imm` (`0x1aa8`)
- `XOR_IMM Rd, imm` (`0x1a90`)
- `ROL_IMM Rd, imm` (`0x1a60`)
- `MOV_REG Rd, Rs` (`0x1a30`)
- `ADD_REG Rd, Rs` (`0x19f0`)
- `SUB_REG Rd, Rs` (`0x19b0`)
- `XOR_REG Rd, Rs` (`0x1988`)
- `LOAD_W Rd, [Rs + imm]` (`0x18d0`)
- `STORE_W [Rs + imm], Rd` (`0x1890`)
- `SBOX Rd` (`0x16a0`): Substitutes high and low bytes of `Rd` via a 256-byte S-box table at `.rodata:0x2160`.

---

## 🔐 Cryptographic Cipher Analysis

The ROM binary reads a 44-byte string (`0x2c` bytes = 22 16-bit words) into `0xc000 .. 0xc02a` and executes an unrolled 10-round cipher. Each round $k \in \{0, \dots, 9\}$ consists of 3 distinct transformations:

1. **Step A (SubBytes & AddRoundKey):**
   $$w_i \leftarrow \text{SBOX}(w_i) \oplus K_{k, i} \quad \forall i \in \{0, \dots, 21\}$$

2. **Step B (Feistel ARX Cascade):**
   $$w_0 \leftarrow (w_0 + w_{21} + 0x5a5a) \bmod 2^{16}$$
   $$w_i \leftarrow (w_i + w_{i-1} + 0x5a5a) \bmod 2^{16} \quad \forall i \in \{1, \dots, 21\}$$

3. **Step C (Cellular Automaton Linear Diffusion Layer):**
   Let $L(x) = x \oplus \text{rol16}(x, 5) \oplus \text{rol16}(x, 11)$.
   $$w_i \leftarrow w_i \oplus L(w_{(i+1)\%22}) \oplus \text{rol16}(L(w_{(i+2)\%22}), k + 1) \quad \forall i \in \{0, \dots, 21\}$$

At the end of round 9, the resulting 22 words are compared word-by-word against expected ciphertext words stored in ROM at `0x7ce3`.

---

## 💻 Analytical Inversion & Solver

Since every step in the cipher is an exact bijection, we can invert the entire 10-round transformation analytically:

1. **Inverting Step C:**
   $$w_i \leftarrow w_i \oplus L(w_{(i+1)\%22}) \oplus \text{rol16}(L(w_{(i+2)\%22}), k + 1) \quad \text{for } i = 21 \text{ down to } 0$$

2. **Inverting Step B:**
   $$w_i \leftarrow (w_i - w_{i-1} - 0x5a5a) \bmod 2^{16} \quad \text{for } i = 21 \text{ down to } 1$$
   $$w_0 \leftarrow (w_0 - w_{21} - 0x5a5a) \bmod 2^{16}$$

3. **Inverting Step A:**
   $$w_i \leftarrow \text{INV\_SBOX}(w_i \oplus K_{k, i}) \quad \forall i \in \{0, \dots, 21\}$$

Running this analytical inversion takes less than **0.01 seconds** and directly outputs the 44-byte flag.

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `ASIS{M1ddL3_3nd14n_N1bbL35_M4k3_Q3MU_D122y!}`

