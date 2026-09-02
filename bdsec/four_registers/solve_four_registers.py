#!/usr/bin/env python3
"""
BDSec CTF 2026 — four_registers solver.

The binary is a tiny 4-register VM. It reads up to 14 assembly lines
("MOVI/ADD/XOR/ROL R<i> <imm>", "SWAP/MIX R<i> R<j>") and terminates on "RUN".
It executes the program on 4 initial 32-bit registers, then checks
    final regs == [0xD0F7F5A4, 0x71D63782, 0x2C458DAC, 0x8C64DE6C]
    carry flag == 1, opcode-usage mask == 0x3F (all 6 ops used),
    FNV-style program hash == 231944115,
and on success derives and prints the 49-byte flag from the execution trace.

This solver models the VM in Z3, solves for a valid 14-instruction program,
re-derives the flag with an independent simulator, and validates the candidate
against the real binary. The flag is the 49 bytes printed after "[+] ".

Usage: python3 solve_four_registers.py [path-to-binary]
"""
import subprocess
import sys
import os

BIN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "four_registers")

M = 16777619          # 0x1000193
MAGIC = 0xA5A5A5A5
HASH0 = 0x811C9DC5
GOLD = 0x61C88647     # 1640531527
INIT = [0x13579BDF, 0x2468ACE0, 0x0BADF00D, 0xC001D00D]
TGT = [0xD0F7F5A4, 0x71D63782, 0x2C458DAC, 0x8C64DE6C]
TGT_HASH = 231944115
OPS = {"MOVI": 19, "ADD": 39, "XOR": 57, "ROL": 75, "SWAP": 93, "MIX": 111}
N = 14
TBL = bytes([
    0x3a, 0xf0, 0x29, 0x08, 0xa5, 0xbb, 0x29, 0x20, 0xcc, 0x99, 0xfd, 0x22, 0x0f, 0x48, 0x03,
    0xa4, 0x95, 0xa3, 0x87, 0x58, 0xda, 0x53, 0x33, 0x34, 0xaf, 0x4b, 0x2b, 0x84, 0x75, 0x36,
    0xd6, 0x07, 0x5b, 0x4d, 0x01, 0xc2, 0xf8, 0x3b, 0xeb, 0x9f, 0xa4, 0x74, 0xf7, 0xe2, 0x43,
    0xd9, 0x87, 0x58, 0x46])


def rol32(x, n):
    x &= 0xFFFFFFFF
    n &= 31
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF if n else x


def rol1(x, n):
    x &= 0xFF
    n &= 7
    return ((x << n) | (x >> (8 - n))) & 0xFF if n else x


def run_vm(prog):
    """prog: list of (name, r1, r2). Returns (regs, mask_carry_info)."""
    regs = INIT[:]
    carry = 0
    mask = 0
    hsh = HASH0
    v29 = 0
    trace = []
    for name, r1, r2 in prog:
        if name == "MOVI":
            regs[r1] = (regs[r1] & 0xFFFFFF00) | (r2 & 0xFF)
            carry = 0
            mask |= 1
        elif name == "ADD":
            v = regs[r1] + carry + r2
            regs[r1] = v & 0xFFFFFFFF
            carry = 1 if v > 0xFFFFFFFF else 0
            mask |= 2
        elif name == "XOR":
            regs[r1] ^= 0x01010101 * r2
            mask |= 4
        elif name == "ROL":
            regs[r1] = rol32(regs[r1], r2)
            mask |= 8
        elif name == "SWAP":
            regs[r1], regs[r2] = regs[r2], regs[r1]
            mask |= 0x10
        elif name == "MIX":
            v = rol32(regs[r2] ^ regs[r1], (regs[r2] & 7) + 1)
            v = (v + carry - GOLD) & 0xFFFFFFFF
            regs[r1] = v
            carry = 1 if (v >> 31) & 1 else 0
            mask |= 0x20
        op = OPS[name]
        v29 = (r2 & 0xFF) ^ rol32(((((r1 ^ rol32(((hsh ^ op) * M) & 0xFFFFFFFF, 5)) ^ MAGIC) * M) & 0xFFFFFFFF), 5)
        hsh = rol32(((v29 ^ MAGIC) * M) & 0xFFFFFFFF, 5) ^ MAGIC
        trace.append((regs[:], carry, hsh))
    return regs, mask, v29, trace


def check_program(prog):
    regs, mask, v29, trace = run_vm(prog)
    carry = trace[-1][1]
    return regs == TGT and carry == 1 and mask == 0x3F and v29 == TGT_HASH


def derive_flag(prog):
    """Replicates the binary's 49-byte flag derivation (objdump 0x1789-0x191f)."""
    regs, mask, v29, trace = run_vm(prog)
    V57 = [[rs[0], rs[1], rs[2], rs[3], hsh, car] for (rs, car, hsh) in trace]
    v40 = 0x9E3779B9
    v41 = V57[0][0] ^ rol32(V57[13][2], 13) ^ rol32(V57[6][1], 7) ^ 0x76177132
    P = lambda i: (OPS[prog[i][0]], prog[i][1], prog[i][2])
    out = []
    for i in range(49):
        A = (9 * i + 4) % 14
        C = (5 * i + 1) % 14
        traceD = V57[C]
        instrA = P(A)
        traceB = V57[A]
        instrC = P(C)
        v47 = (traceD[(i + instrA[1]) & 3] ^ v41) + rol32(traceB[4], i % 13 + 1)
        v47 = (v47 & 0xFFFFFFFF) ^ ((instrC[0] << 24) | (instrC[1] << 16) | ((instrA[2] & 0xFF) << 8) | traceB[5])
        x = v47
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        x &= 0xFFFFFFFF
        v41 = (v40 + ((32 * x) ^ x)) & 0xFFFFFFFF
        v49 = rol1(instrA[2] & 0xFF, i)
        m = 0xA7 if traceD[5] != 0 else 0
        b = (m ^ v49 ^ v41 ^ ((v41 >> 24) & 0xFF) ^ ((v41 >> 8) & 0xFF) ^ ((v41 >> 16) & 0xFF)
             ^ (instrA[0] ^ TBL[i] ^ ((29 * instrC[2]) & 0xFF))) & 0xFF
        out.append(b)
        v40 = (v40 + 0x45D9F3B) & 0xFFFFFFFF
    return bytes(out)


def find_program():
    from z3 import (BitVec, BitVecVal, Solver, Or, And, ULE, UGE, If, Concat, Extract,
                    ZeroExt, RotateLeft, sat, Implies)

    def rol32z(x, n):
        return RotateLeft(x, n)

    s = Solver()
    ops = [BitVec(f"op{i}", 8) for i in range(N)]
    r1s = [BitVec(f"r1{i}", 8) for i in range(N)]
    r2s = [BitVec(f"r2{i}", 8) for i in range(N)]
    for i in range(N):
        op, r1, r2 = ops[i], r1s[i], r2s[i]
        s.add(Or(*[op == c for c in OPS.values()]))
        s.add(ULE(r1, 3))
        s.add(Implies(op == OPS["ROL"], And(UGE(r2, 1), ULE(r2, 31))))
        s.add(Implies(op == OPS["MOVI"], ULE(r2, 0xFF)))
        s.add(Implies(op == OPS["ADD"], ULE(r2, 0xFF)))
        s.add(Implies(op == OPS["XOR"], ULE(r2, 0xFF)))
        s.add(Implies(op == OPS["SWAP"], And(ULE(r2, 3), r2 != r1)))
        s.add(Implies(op == OPS["MIX"], And(ULE(r2, 3), r2 != r1)))
    for c in OPS.values():
        s.add(Or(*[ops[i] == c for i in range(N)]))
    regs = [BitVecVal(x, 32) for x in INIT]
    carry = BitVecVal(0, 1)
    hsh = BitVecVal(HASH0, 32)
    v29 = None

    def rread(r):
        return If(r == 0, regs[0], If(r == 1, regs[1], If(r == 2, regs[2], regs[3])))

    for i in range(N):
        op, r, r2 = ops[i], r1s[i], r2s[i]
        va = rread(r)
        vb = rread(r2)
        movi = Concat(Extract(31, 8, va), r2)
        z64 = lambda x: ZeroExt(64 - x.size(), x)
        asum = z64(va) + z64(carry) + z64(r2)
        addv = Extract(31, 0, asum)
        addc = Extract(32, 32, asum)
        xorv = va ^ Concat(r2, Concat(r2, Concat(r2, r2)))
        rolv = rol32z(va, ZeroExt(24, r2))
        mixv = rol32z(vb ^ va, (vb & 7) + 1) + ZeroExt(31, carry) - BitVecVal(GOLD, 32)
        mixc = Extract(31, 31, mixv)
        sw = [If(r == j, vb, If(r2 == j, va, regs[j])) for j in range(4)]
        mov = [If(r == j, movi, regs[j]) for j in range(4)]
        add = [If(r == j, addv, regs[j]) for j in range(4)]
        xor = [If(r == j, xorv, regs[j]) for j in range(4)]
        rol = [If(r == j, rolv, regs[j]) for j in range(4)]
        mix = [If(r == j, mixv, regs[j]) for j in range(4)]
        regs = [If(op == OPS["SWAP"], sw[j], If(op == OPS["MOVI"], mov[j],
                If(op == OPS["ADD"], add[j], If(op == OPS["XOR"], xor[j],
                If(op == OPS["ROL"], rol[j], mix[j]))))) for j in range(4)]
        carry = If(op == OPS["SWAP"], carry, If(op == OPS["MOVI"], BitVecVal(0, 1),
                If(op == OPS["ADD"], addc, If(op == OPS["XOR"], carry,
                If(op == OPS["ROL"], carry, mixc)))))
        t = rol32z((hsh ^ ZeroExt(24, op)) * M, 5)
        t = rol32z((ZeroExt(24, r) ^ t ^ MAGIC) * M, 5)
        v29 = ZeroExt(24, r2) ^ t
        hsh = rol32z(((v29 ^ MAGIC) * M), 5) ^ MAGIC
    for j in range(4):
        s.add(regs[j] == TGT[j])
    s.add(carry == 1)
    s.add(v29 == TGT_HASH)
    print("[*] Z3 solving ...", flush=True)
    if s.check() != sat:
        return None
    m = s.model()
    inv = {v: k for k, v in OPS.items()}
    return [(inv[m.eval(ops[i]).as_long()], m.eval(r1s[i]).as_long(), m.eval(r2s[i]).as_long())
            for i in range(N)]


def to_asm(prog):
    lines = [f"{n} R{a} R{b}" if n in ("SWAP", "MIX") else f"{n} R{a} {b}"
             for (n, a, b) in prog]
    lines.append("RUN")
    return "\n".join(lines) + "\n"


def main():
    prog = find_program()
    if prog is None:
        print("[-] no program found")
        sys.exit(1)
    for i, (n, a, b) in enumerate(prog):
        print(f"  {i:2d}: {n:4} R{a} {b}")
    ok = check_program(prog)
    print("[*] sim check:", ok)
    flag = derive_flag(prog)
    print("[*] derived flag:", flag.decode(errors="replace"))
    out = subprocess.run([BIN], input=to_asm(prog), capture_output=True, text=True, timeout=20).stdout
    m = out.find("[+] ")
    if m >= 0:
        bf = out[m + 4:].strip()
        print("[+] binary says:", bf)
        assert bf.encode() == flag, "sim/binary mismatch!"
    else:
        print("[!] binary did not print a flag; tail:", out.strip().splitlines()[-3:])
    return flag


if __name__ == "__main__":
    main()