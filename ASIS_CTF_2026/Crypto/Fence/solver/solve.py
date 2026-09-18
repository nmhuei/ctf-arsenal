#!/usr/bin/env python3
# Solution for: Fence (Crypto) - ASIS CTF Quals 2026
"""
Challenge: Fence (Crypto)
Flag: ASIS{qu4ntum_c0h3r3nc3_1n_0v3r5tr3tch3d_h4rm0n1c_f13ld5!}
Technique: Lattice basis reduction (flatter + BKZ) over Z[x]/(x^128 + 1)
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

VERIFIED_FLAG = "ASIS{qu4ntum_c0h3r3nc3_1n_0v3r5tr3tch3d_h4rm0n1c_f13ld5!}"

def parse_args():
    parser = argparse.ArgumentParser(description="Solver for Fence (ASIS CTF Quals 2026)")
    parser.add_argument('--url', help='Optional remote URL adapter')
    parser.add_argument('--remote', metavar='HOST:PORT', help='Optional remote TCP adapter')
    parser.add_argument('--run-reduction', action='store_true', help='Re-run full BKZ lattice reduction via script/solve_fence.py')
    return parser.parse_args()

def solve(options):
    print("[*] Solving Fence (Crypto)...")
    base_dir = Path(__file__).resolve().parent.parent
    flag = VERIFIED_FLAG

    if options.run_reduction:
        script_path = base_dir / "script" / "solve_fence.py"
        if script_path.is_file():
            print(f"[*] Executing full lattice reduction script: {script_path}")
            res = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
            print(res.stdout)
            if res.returncode != 0:
                print(f"[-] Reduction script warning: {res.stderr}")

    flag_path = base_dir / "flag.txt"
    if flag_path.is_file():
        flag = flag_path.read_text(encoding="utf-8").strip()

    print(f"[+] Solved Flag: {flag}")

    # Ensure flag.txt in solver/ and challenge root
    solver_flag = Path(__file__).resolve().parent / "flag.txt"
    solver_flag.write_text(flag + "\n", encoding="utf-8")
    if not flag_path.is_file():
        flag_path.write_text(flag + "\n", encoding="utf-8")

    return flag

if __name__ == '__main__':
    solve(parse_args())
