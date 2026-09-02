#!/usr/bin/env python3
"""Simulate the binary's flag-printing loop (from decompilation) for a program,
returning the 49 printed bytes. Used to pre-screen solver candidates."""
import sys

OPS = {"MOVI": 0x13, "ADD": 0x27, "XOR": 0x39, "ROL": 0x4B, "SWAP": 0x5D, "MIX": 0x6F}
M = 0x1000193
MAGIC = 0xA5A5A5A5
HASH0 = 0x811C9DC5
GOLD = 0x61C88647
INIT = [0x13579BDF, 0x2468ACE0, 0x0BADF00D, 0xC001D00D]
TBL = bytes([0x3a,0xf0,0x29,0x08,0xa5,0xbb,0x29,0x20,0xcc,0x99,0xfd,0x22,0x0f,0x48,0x03,
             0xa4,0x95,0xa3,0x87,0x58,0xda,0x53,0x33,0x34,0xaf,0x4b,0x2b,0x84,0x75,0x36,
             0xd6,0x07,0x5b,0x4d,0x01,0xc2,0xf8,0x3b,0xeb,0x9f,0xa4,0x74,0xf7,0xe2,0x43,
             0xd9,0x87,0x58,0x46])

def rol32(x, n):
    x &= 0xFFFFFFFF
    n &= 31
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF if n else x

def sim(prog):
    """prog: list of (name, r1, r2). Returns final state + per-step trace.
    trace[k] = dict(regs=[4], carry, hsh)"""
    regs = INIT[:]
    carry = 0; hsh = HASH0
    trace = []
    for name, r1, r2 in prog:
        va = regs[r1]
        if name == "MOVI":
            regs[r1] = (regs[r1] & 0xFFFFFF00) | r2; carry = 0
        elif name == "ADD":
            s = va + carry + r2; regs[r1] = s & 0xFFFFFFFF; carry = 1 if s > 0xFFFFFFFF else 0
        elif name == "XOR":
            regs[r1] = (va ^ (r2 * 0x01010101)) & 0xFFFFFFFF
        elif name == "ROL":
            regs[r1] = rol32(va, r2)
        elif name == "SWAP":
            regs[r1], regs[r2] = regs[r2], regs[r1]
        elif name == "MIX":
            vb = regs[r2]
            t = rol32(vb ^ va, (vb & 7) + 1) + carry - GOLD
            regs[r1] = t & 0xFFFFFFFF
            carry = 1 if (t >> 31) & 1 else 0
        t = rol32((hsh ^ OPS[name]) * M, 5)
        t = rol32((r1 ^ t ^ MAGIC) * M, 5)
        v29 = (r2 ^ t) & 0xFFFFFFFF
        hsh = (rol32(((v29 ^ MAGIC) * M), 5) ^ MAGIC) & 0xFFFFFFFF
        trace.append(dict(regs=regs[:], carry=carry, hsh=hsh))
    return regs, carry, hsh, trace

def print_flag(prog, trace):
    """Emulate the 49-byte print loop."""
    # trace is 14 records; hash slot = hsh after each instr; carry slot = carry byte
    v41 = trace[0]["regs"][0] ^ rol32(trace[13]["regs"][2], 13) ^ rol32(trace[6]["regs"][1], 7) ^ 0x76177132
    v40 = -1640531527 & 0xFFFFFFFF
    out = bytearray()
    for m in range(49):
        k1 = (5 * m + 1) % 14
        j2 = (9 * m + 4) % 14
        instr_k1 = prog[k1]
        instr_j2 = prog[j2]
        r1_j2 = instr_j2[1]
        regsel = trace[k1]["regs"][(m + r1_j2) & 3]
        jhash = trace[j2]["hsh"]
        v47 = ((regsel ^ v41) + rol32(jhash, (m % 13) + 1)) & 0xFFFFFFFF
        mask = (instr_j2[2] << 8) | (trace[j2]["carry"] & 0xFF) | (instr_k1[1] << 16) | (OPS[instr_k1[0]] << 24)
        v47 ^= mask
        v48 = ((((v47 << 13) ^ v47) >> 17) ^ (v47 << 13) ^ v47) & 0xFFFFFFFF
        v41 = (v40 + ((32 * v48) ^ v48)) & 0xFFFFFFFF
        v49 = rol32(instr_j2[2], m) & 0xFF
        v43 = TBL[m] ^ OPS[instr_j2[0]]
        c2 = 0xA7 if trace[j2]["carry"] else 0
        b = c2 ^ ((v41 >> 24) & 0xFF) ^ ((v41 >> 8) & 0xFF) ^ (v41 & 0xFF) ^ v49 \
            ^ ((29 * instr_k1[2]) & 0xFF) ^ v43 ^ ((v41 >> 16) & 0xFF)
        out.append(b & 0xFF)
        v40 = (v40 + 73244475) & 0xFFFFFFFF
    return bytes(out)

if __name__ == "__main__":
    # sanity: parse asm file lines like "MOVI R0 12" / "SWAP R0 R1" / "VEN" ignored
    lines = [l.strip().split() for l in open(sys.argv[1]) if l.strip()]
    prog = []
    for toks in lines:
        if toks[0].upper() == "VEN":
            continue
        name = toks[0].upper()
        r1 = int(toks[1][1:])
        r2 = int(toks[2][1:]) if toks[2].startswith("R") else int(toks[2], 0)
        prog.append((name, r1, r2))
    regs, carry, hsh, trace = sim(prog)
    print("final regs:", [hex(x) for x in regs], "carry", carry, "hsh", hex(hsh))
    fl = print_flag(prog, trace)
    print("flag bytes:", fl)
    print("flag repr :", repr(fl))