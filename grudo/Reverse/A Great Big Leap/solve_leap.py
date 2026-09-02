#!/usr/bin/env python3
"""A Great Big Leap — find the largest relative jump (the "great big leap").

Uses objdump -d output (proper instruction-boundary decoding) and computes
displacement = target - (address + size) for every direct branch.
The flag is the largest absolute displacement, in hex: grodno{123}.
"""
import re
import subprocess
import sys


def solve(path):
    out = subprocess.run(["objdump", "-d", "-Mintel", path],
                         capture_output=True, text=True).stdout
    jumps = []  # (abs_disp, addr, mnemonic, target)
    for line in out.splitlines():
        m = re.match(r"\s*([0-9a-f]+):\s+([0-9a-f ]+)\t(\S+)(.*)$", line)
        if not m:
            continue
        addr = int(m.group(1), 16)
        mnem = m.group(3)
        if not mnem.startswith("j"):
            continue
        rest = m.group(4).strip()
        if "PTR" in rest or rest.startswith("*"):
            continue  # indirect (absolute/memory) jump — not a relative branch
        # operand: target address for near jumps
        tm = re.search(r"([0-9a-f]+)\s*$", rest)
        if not tm:
            continue
        target = int(tm.group(1), 16)
        size = len(m.group(2).split())
        disp = target - (addr + size)
        jumps.append((abs(disp), addr, mnem, disp, target))
    dist, addr, mnem, disp, target = max(jumps, key=lambda j: j[0])
    print(f"largest jump: {addr:#x} ({mnem}) -> {target:#x}  disp={disp:+d} (0x{dist:x})")
    print(f"FLAG: grodno{{{dist:x}}}")


if __name__ == "__main__":
    solve(sys.argv[1] if len(sys.argv) > 1 else "/tmp/re/leap/goingtoofaraway5.exe")
