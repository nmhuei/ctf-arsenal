# Writeup: ASIS Arch

| Property | Value |
| :--- | :--- |
| **Category** | `Reverse` |
| **Points** | `34` |
| **Author** | `-` |
| **Solves** | `203` |

---

## 📝 Challenge Overview

We are given a custom CPU emulator binary (`qemu-asisarch`) and a secure ROM image (`challenge.rom`).
Running the emulator:
```bash
./qemu-asisarch -M asisboard -kernel challenge.rom -nographic
```
prompts for a flag:
```
=== ASISARCH Secure Enclave v2.0 ===
Enter flag:
```
Incorrect inputs trigger `[-] Access Denied. Invalid flag.`, while the correct flag prints `[+] Access Granted! Flag verified.`.

---

## 🔍 Architecture & ISA Reverse Engineering

### 1. Emulator Disassembly & VM State

Reversing `qemu-asisarch` reveals that it is not full QEMU, but a lightweight 64-bit ELF executable implementing an emulator for a custom 16-bit RISC-like architecture dubbed **ASISARCH**:
- **Memory space**: 64 KB (`0x0000` - `0xFFFF`).
- **Registers**: 8 general-purpose 16-bit registers: `r0` through `r7`.
- **Special registers**:
  - Stack Pointer `SP`: 16-bit, initialized to `0xFFF0` (stack grows downward).
  - Program Counter `PC`: 16-bit, initialized from the ROM header (here `0x0000`).
  - Cycle counter: 64-bit, checked against a limit of `10,000,000` cycles.
- **ROM format**:
  - Magic: `AARQ` (`0x51524141`)
  - Version: `2`
  - Encoded initial PC at offset `0x08..0x09`
  - Checksum at offset `0x0C..0x0F`
  - Code/Data payload starting at offset `0x20`, mapped to memory base `0x0000`.

### 2. Instruction Encoding & Decoding

Instructions are 4 bytes (32 bits) fixed-length, executed from `PC`. Each instruction is obfuscated based on the current `PC` and an instruction permutation table:
```python
ax = (pc ^ 0x9e37) & 0xffff
ax = (ax * 0x1039 + 0x79b9) & 0xffff
edi = ax
perm_idx = (ax >> 14) & 3
di = rol16(edi, 5)

# 4-byte byte-permutation
p = [[0, 1, 2, 3], [2, 0, 3, 1], [3, 2, 1, 0], [1, 3, 0, 2]][perm_idx]
r9d = mem[pc + p[0]]
r8d = mem[pc + p[1]]
m2  = mem[pc + p[2]]
edx = mem[pc + p[3]]

# Opcode derivation
al = (((0x5d * pc) ^ di ^ m2) & 0xff)
al = rol8(al, (di >> 5) & 7) ^ 0x6d
opcode = al

# Operand & Register derivation
ecx = (di >> 2) & 0xffff
eax = ((pc * 7) ^ ecx) & 0xffffffff
r8b = rol8((r8d ^ di) & 0xff, 4)
eax ^= r8b ^ r9d
al = eax & 0xff
rd = (((((al * 5) ^ 3) & 7) * 5) ^ 3) & 7

dl = rol8((edx ^ (di >> 8)) & 0xff, 4)
imm16 = rol16((dl << 8) | r8b, 5)
rs = (((imm16 & 7) * 5) ^ 3) & 7
offset = imm16 >> 3
```

### 3. Opcode Set

The emulator features a 26-entry opcode jump table:
- `0x10`: `NOP`
- `0x15`: `MOV_IMM rd, imm16`
- `0x21`: `ADD_IMM rd, imm16`
- `0x27`: `SUB_IMM rd, imm16`
- `0x32`: `XOR_IMM rd, imm16`
- `0x38`: `AND_IMM rd, imm16`
- `0x44`: `ROL_IMM rd, imm5`
- `0x4b`: `MOV_REG rd, rs`
- `0x50`: `ADD_REG rd, rs`
- `0x56`: `SUB_REG rd, rs`
- `0x5c`: `XOR_REG rd, rs`
- `0x63`: `LOAD8 rd, [rs + offset]`
- `0x69`: `STORE8 rd, [rs + offset]`
- `0x71`: `LOAD16 rd, [rs + offset]`
- `0x77`: `STORE16 rd, [rs + offset]`
- `0x80`: `JMP imm16`
- `0x86`: `JZ rd, imm16`
- `0x8c`: `JNZ rd, imm16`
- `0x92`: `PUSH rd`
- `0x98`: `POP rd`
- `0xa1`: `CALL imm16`
- `0xa7`: `RET`
- `0xb3`: `GETC rd`
- `0xb9`: `PUTC rd`
- `0xc2`: `SBOX rd` (substitutes high and low bytes of `rd` through a bijective 256-byte S-box at `0x2160`)
- `0xfe`: `HALT`

---

## 🔬 Cryptographic Verification Analysis

### 1. Input Processing
- Input buffer is located at `0xc000`.
- The flag length must be exactly `44` bytes (`0x2c`).
- The 44 bytes are interpreted as `22` 16-bit little-endian words: `buf[0]` through `buf[21]`.

### 2. The 10-Round Cipher Structure
The verification code executes 10 iterations ($k = 0 \dots 9$) of a 3-layer cipher:

1. **Layer A (Substitution & Key Mixing)**:
   For $i = 0 \dots 21$:
   $$\text{buf}[i] \leftarrow \text{SBOX}(\text{buf}[i]) \oplus \text{KEY}[k][i]$$
2. **Layer B (Modular Addition Diffusion)**:
   $$\text{buf}[0] \leftarrow (\text{buf}[0] + \text{buf}[21] + 0x5a5a) \pmod{2^{16}}$$
   For $i = 1 \dots 21$:
   $$\text{buf}[i] \leftarrow (\text{buf}[i] + \text{buf}[i-1] + 0x5a5a) \pmod{2^{16}}$$
3. **Layer C (Cellular Linear Diffusion)**:
   Defining $\theta(x) = x \oplus (x \lll 5) \oplus (x \lll 11)$:
   For $i = 0 \dots 21$:
   $$\text{buf}[i] \leftarrow \text{buf}[i] \oplus \theta(\text{buf}[(i+1) \pmod{22}]) \oplus (\theta(\text{buf}[(i+2) \pmod{22}]) \lll (k+1))$$

### 3. Target State
At the end of round 9 (Layer C with shift 10), each word is compared against target values loaded from ROM at `0x7cdb`:
$$\text{Target}[i] = \text{ROM}_{16}[0x7cdb + \text{offset}_i] \oplus \text{ROM}_{16}[0x7cdb + \text{offset}_i + 2]$$

---

## 💻 Inversion & Exploitation Strategy

Every layer is directly invertible:

1. **Inverse Layer C**:
   Because elements in the forward pass update from $i = 0$ to $21$, reversing from $i = 21$ down to $0$ uses the exact known surrounding states:
   $$\text{buf}[i] \leftarrow \text{buf}[i] \oplus \theta(\text{buf}[(i+1) \pmod{22}]) \oplus (\theta(\text{buf}[(i+2) \pmod{22}]) \lll (k+1))$$
2. **Inverse Layer B**:
   $$\text{buf}[i] \leftarrow (\text{buf}[i] - \text{buf}[i-1] - 0x5a5a) \pmod{2^{16}} \quad \text{for } i = 21, 20, \dots, 1$$
   $$\text{buf}[0] \leftarrow (\text{buf}[0] - \text{buf}[21] - 0x5a5a) \pmod{2^{16}}$$
3. **Inverse Layer A**:
   $$val = \text{buf}[i] \oplus \text{KEY}[k][i]$$
   $$\text{buf}[i] = (\text{SBOX}^{-1}[val \gg 8] \ll 8) \mid \text{SBOX}^{-1}[val \ \& \ 0xff]$$

Running this inversion backward from $k=9$ down to $k=0$ recovers the original input words.

Full solver is in [`solver/solve.py`](../solver/solve.py):
```bash
python3 ../solver/solve.py
```

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `ASIS{M1ddL3_3nd14n_N1bbL35_M4k3_Q3MU_D122y!}`
