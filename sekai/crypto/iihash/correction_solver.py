#!/usr/bin/env python3
"""
Phase 6: Correction lane pair solver
Solves the decoupled HIGH and LOW equations to find the 8 words of stripe 4.
"""

import os
import subprocess
from inverse_avalanche import get_desired_merge_state

DIR = os.path.dirname(os.path.abspath(__file__))
SOLVER_BIN = os.path.join(DIR, "vow_solver")
SOLVER_SRC = os.path.join(DIR, "vow_solver.c")

def ensure_solver_compiled():
    if not os.path.exists(SOLVER_BIN) or os.path.getmtime(SOLVER_SRC) > os.path.getmtime(SOLVER_BIN):
        print("[*] Compiling vow_solver.c...")
        subprocess.run(["gcc", "-O3", "-pthread", SOLVER_SRC, "-o", SOLVER_BIN], check=True)

def solve_correction(seed: int, target_digest: bytes = b"Give me the flag") -> list[int]:
    """
    Solves for the 8 words [w0, w1, w2, w3, w4, w5, w6, w7] such that
    accumulating stripe 4 onto 4 zero stripes yields the desired merge state.
    """
    ensure_solver_compiled()
    target_sum_low, target_sum_high = get_desired_merge_state(target_digest, 320)
    cmd = [
        SOLVER_BIN,
        hex(seed),
        hex(target_sum_low),
        hex(target_sum_high),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    out = proc.stdout.strip().split()
    assert len(out) == 8, f"Expected 8 words, got {out}"
    words = [int(x, 16) for x in out]
    return words

if __name__ == "__main__":
    print("[*] Testing correction_solver interface...")
    ensure_solver_compiled()
    print("[+] Solver compiled and ready.")
