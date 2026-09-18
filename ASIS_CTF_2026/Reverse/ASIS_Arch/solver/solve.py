#!/usr/bin/env python3
"""
Solution for: ASIS Arch (Reverse) - ASIS CTF Quals 2026
Flag: ASIS{M1ddL3_3nd14n_N1bbL35_M4k3_Q3MU_D122y!}
"""
import os
import subprocess
from pathlib import Path

def rol8(v, n):
    n &= 7
    return ((v << n) | (v >> (8 - n))) & 0xff

def rol16(v, n):
    n &= 15
    return ((v << n) | (v >> (16 - n))) & 0xffff

def theta(x):
    return x ^ rol16(x, 5) ^ rol16(x, 11)

TABLE_PERM = [
    [0, 1, 2, 3],
    [2, 0, 3, 1],
    [3, 2, 1, 0],
    [1, 3, 0, 2],
]

OPCODES = {
    0x10: 'NOP', 0x15: 'MOV_IMM', 0x21: 'ADD_IMM', 0x27: 'SUB_IMM', 0x32: 'XOR_IMM',
    0x38: 'AND_IMM', 0x44: 'ROL_IMM', 0x4b: 'MOV_REG', 0x50: 'ADD_REG', 0x56: 'SUB_REG',
    0x5c: 'XOR_REG', 0x63: 'LOAD8', 0x69: 'STORE8', 0x71: 'LOAD16', 0x77: 'STORE16',
    0x80: 'JMP', 0x86: 'JZ', 0x8c: 'JNZ', 0x92: 'PUSH', 0x98: 'POP', 0xa1: 'CALL',
    0xa7: 'RET', 0xb3: 'GETC', 0xb9: 'PUTC', 0xc2: 'SBOX', 0xfe: 'HALT',
}

def decode_insn(mem, pc):
    esi = pc
    ax = (pc ^ 0x9e37) & 0xffff
    ax = (ax * 0x1039) & 0xffff
    ax = (ax + 0x79b9) & 0xffff
    edi = ax
    perm_idx = (ax >> 14) & 3
    di = rol16(edi, 5)
    edi = di
    
    p = TABLE_PERM[perm_idx]
    r9d = mem[pc + p[0]]
    r8d = mem[pc + p[1]]
    m2 = mem[pc + p[2]]
    edx = mem[pc + p[3]]
    
    eax = (0x5d * esi) & 0xffffffff
    eax ^= edi
    al = (eax ^ m2) & 0xff
    
    cx = (edi >> 5) & 0xffff
    al = rol8(al, cx & 7)
    al ^= 0x6d
    opcode = al
    
    ecx = edi
    eax = (esi * 8) & 0xffffffff
    r8d ^= edi
    cx = (edi >> 2) & 0xffff
    ecx = cx
    eax = (eax - esi) & 0xffffffff
    r8b = rol8(r8d & 0xff, 4)
    eax ^= ecx
    r8d = r8b
    eax ^= r9d
    al = eax & 0xff
    
    eax = ((al * 5) ^ 3) & 7
    r14d = (eax * 5) ^ 3
    rd = r14d & 7
    
    ah = (edi >> 8) & 0xff
    dl = (edx ^ ah) & 0xff
    dl = rol8(dl, 4)
    edx = (dl << 8) | r8d
    dx = rol16(edx & 0xffff, 5)
    imm16 = dx
    
    rs = (((imm16 & 7) * 5) ^ 3) & 7
    offset = imm16 >> 3
    
    return opcode, rd, imm16, rs, offset

def solve():
    base_dir = Path(__file__).resolve().parent.parent
    rom_path = base_dir / 'challenge' / 'ASIS-Arch' / 'challenge.rom'
    emu_path = base_dir / 'challenge' / 'ASIS-Arch' / 'qemu-asisarch'

    with open(rom_path, 'rb') as f:
        rom = f.read()
    payload = rom[0x20:]
    mem = bytearray(0x10000)
    mem[:len(payload)] = payload

    with open(emu_path, 'rb') as f:
        qemu_data = f.read()
    sbox = qemu_data[0x2160:0x2260]
    inv_sbox = [0] * 256
    for i, v in enumerate(sbox):
        inv_sbox[v] = i

    # Extract Layer A keys from the 10 Layer A rounds
    layer_a_rounds = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27]
    stores = []
    for pc in range(0x0024, 0x7874, 4):
        op, rd, imm16, rs, off = decode_insn(mem, pc)
        if OPCODES.get(op) == 'STORE16':
            stores.append(pc)

    all_layer_a_keys = []
    for r in layer_a_rounds:
        keys = []
        r_stores = stores[r * 22 : (r + 1) * 22]
        for st_pc in r_stores:
            for p in range(st_pc - 16, st_pc, 4):
                op, rd, imm16, rs, off = decode_insn(mem, p)
                if OPCODES.get(op) == 'MOV_IMM' and rd == 1:
                    keys.append(imm16)
        all_layer_a_keys.append(keys)

    # Extract target expected values
    offsets = [
        0x0008, 0x0050, 0x0028, 0x0038, 0x0010, 0x0090, 0x0018, 0x0088,
        0x00a8, 0x0040, 0x00a0, 0x0080, 0x0070, 0x0068, 0x0048, 0x0030,
        0x0078, 0x0058, 0x0098, 0x0000, 0x0020, 0x0060
    ]
    base = 0x7cdb
    buf = []
    for off in offsets:
        addr = base + off
        w1 = payload[addr] | (payload[addr + 1] << 8)
        w2 = payload[addr + 2] | (payload[addr + 3] << 8)
        buf.append(w1 ^ w2)

    # Invert 10 rounds from k = 9 down to 0
    for k in range(9, -1, -1):
        # 1. Inverse Layer C (cellular diffusion step)
        shift = k + 1
        for i in range(21, -1, -1):
            t1 = theta(buf[(i + 1) % 22])
            t2 = rol16(theta(buf[(i + 2) % 22]), shift)
            buf[i] ^= t1 ^ t2

        # 2. Inverse Layer B (cyclic modular addition step)
        for i in range(21, 0, -1):
            buf[i] = (buf[i] - buf[i - 1] - 0x5a5a) & 0xffff
        buf[0] = (buf[0] - buf[21] - 0x5a5a) & 0xffff

        # 3. Inverse Layer A (S-box + XOR key)
        keys = all_layer_a_keys[k]
        for i in range(22):
            val = buf[i] ^ keys[i]
            hi = inv_sbox[(val >> 8) & 0xff]
            lo = inv_sbox[val & 0xff]
            buf[i] = (hi << 8) | lo

    flag_bytes = bytearray()
    for w in buf:
        flag_bytes.append(w & 0xff)
        flag_bytes.append((w >> 8) & 0xff)

    flag = flag_bytes.decode('utf-8')
    print(f'[+] Recovered Flag: {flag}')

    # Verify directly with emulator
    if os.path.exists(emu_path):
        proc = subprocess.run(
            [str(emu_path), '-M', 'asisboard', '-kernel', str(rom_path), '-nographic'],
            input=f'{flag}\n',
            capture_output=True,
            text=True
        )
        if 'Access Granted' in proc.stdout:
            print('[+] Local verification: PASSED (Access Granted)')
        else:
            print(f'[-] Local verification: FAILED ({proc.stdout.strip()})')

    return flag

if __name__ == '__main__':
    solve()
