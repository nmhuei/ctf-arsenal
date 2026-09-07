#!/usr/bin/env python3
"""
Crypto/1+1 Solver Wrapper
Runs solve.sage via SageMath or Python with sage environment.
"""
import subprocess
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAGE_SCRIPT = os.path.join(SCRIPT_DIR, "solve.sage")
SAGE_BIN = "/home/light/miniforge3/envs/sage/bin/sage"

def solve():
    if not os.path.exists(SAGE_BIN):
        sage_cmd = "sage"
    else:
        sage_cmd = SAGE_BIN
    print(f"[*] Running {SAGE_SCRIPT} with {sage_cmd}...")
    proc = subprocess.run([sage_cmd, SAGE_SCRIPT], capture_output=True, text=True)
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    return proc.returncode

if __name__ == '__main__':
    solve()
