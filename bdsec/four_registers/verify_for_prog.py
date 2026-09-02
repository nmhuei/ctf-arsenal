#!/usr/bin/env python3
"""four_registers — verify a candidate assembly program against the real binary
and print whatever flag the binary emits. Usage: python3 verify.py <asmfile> [bin]"""
import subprocess, sys, re

def run(asm_lines, binpath):
    data = "\n".join(asm_lines) + "\n"
    out = subprocess.run([binpath], input=data, capture_output=True, text=True, timeout=10)
    return out.stdout, out.stderr, out.returncode

def main():
    asmfile = sys.argv[1]
    binpath = sys.argv[2] if len(sys.argv) > 2 else "/tmp/re/four/four_registers"
    lines = [l.strip() for l in open(asmfile).read().splitlines() if l.strip()]
    out, err, rc = run(lines, binpath)
    print("exit:", rc)
    print(out)
    if err:
        print("stderr:", err)
    m = re.search(r"\[[+]\]\s*(\S+)", out)
    if m:
        print("FLAG:", m.group(1))

if __name__ == "__main__":
    main()