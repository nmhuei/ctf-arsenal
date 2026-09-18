#!/usr/bin/env sage
import json
import subprocess
import re
import hashlib
import hmac
import sys
import time
from pathlib import Path

import os
chal_dir = "/home/light/Workspace/CTF/ASIS_CTF_2026/Crypto/Fence/challenge/Fence"
if chal_dir not in sys.path:
    sys.path.insert(0, chal_dir)
from fence import dc, q, n

try:
    from fpylll import IntegerMatrix, BKZ
except ImportError:
    print("fpylll not available! Run via sage.")
    sys.exit(1)

STRAT_PATH = "/home/light/miniforge3/envs/sage/share/fplll/strategies/default.json"

def solve_lock(h_poly, ciphertext, lock_idx):
    print(f"\n[+] Solving Lock {lock_idx + 1}/5...")
    t0 = time.time()

    # Step 1: Build circulant matrix H for multiplication modulo (X^n + 1)
    cur = list(h_poly)
    H_rows = [cur]
    for _ in range(1, n):
        cur = [(-cur[-1]) % q] + cur[:-1]
        H_rows.append(cur)

    # Step 2: Form 256x256 basis: [q*I, 0; H, I]
    matrix_rows = []
    for i in range(n):
        row = [0] * (2 * n)
        row[i] = q
        matrix_rows.append(row)
    for i in range(n):
        row = list(H_rows[i]) + [0] * n
        row[n + i] = 1
        matrix_rows.append(row)

    lines = ["["]
    for r in matrix_rows:
        lines.append("[" + " ".join(map(str, r)) + "]")
    lines.append("]")
    matrix_str = "\n".join(lines)

    # Step 3: Run flatter (fast LLL)
    print("    Running flatter...")
    tf0 = time.time()
    p = subprocess.run(["flatter"], input=matrix_str, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"Flatter failed: {p.stderr}")
    tf1 = time.time()
    print(f"    Flatter completed in {tf1 - tf0:.2f}s")

    nums = list(map(int, re.findall(r'-?\d+', p.stdout)))
    small_rows = []
    for i in range(2 * n):
        row = nums[i * 2 * n : (i + 1) * 2 * n]
        if sum(x**2 for x in row)**0.5 < 1000:
            small_rows.append(row)

    print(f"    Isolated {len(small_rows)} basis vectors in target ideal submodule")

    # Step 4: BKZ reduction on the small submodule
    B = IntegerMatrix(len(small_rows), 2 * n)
    for i in range(len(small_rows)):
        for j in range(2 * n):
            B[i, j] = small_rows[i][j]

    tb0 = time.time()
    found_norm = False
    for bs in [15, 20, 25, 30, 35, 40, 45, 50]:
        BKZ.reduction(B, BKZ.Param(block_size=bs, strategies=STRAT_PATH, max_loops=4))
        min_sq = min(sum(B[i, j]**2 for j in range(2 * n)) for i in range(len(small_rows)))
        print(f"      BKZ-{bs} finished: min_norm_sq = {min_sq}")
        if min_sq == 160:
            found_norm = True
            break

    tb1 = time.time()
    print(f"    BKZ search completed in {tb1 - tb0:.2f}s")

    # Step 5: Extract vector of norm^2 == 160
    target_row = None
    for i in range(len(small_rows)):
        norm_sq = sum(B[i, j]**2 for j in range(2 * n))
        if norm_sq == 160:
            target_row = [B[i, j] for j in range(2 * n)]
            break

    if not target_row:
        # Check smallest norm
        norms = [(sum(B[i, j]**2 for j in range(2 * n)), i) for i in range(len(small_rows))]
        norms.sort()
        print(f"    Smallest norm_sq: {norms[:3]}")
        raise ValueError(f"Could not find vector of norm^2=160 for lock {lock_idx}")

    b_found = target_row[:n]
    a_found = target_row[n:]
    print("    Found shortest vector! Attempting decryption...")

    # Step 6: Decrypt ciphertext
    m = None
    for a_cand, b_cand in [(a_found, b_found), ([-x for x in a_found], [-x for x in b_found])]:
        try:
            m = dc(a_cand, b_cand, h_poly, ciphertext)
            break
        except Exception:
            continue

    if m is None:
        raise ValueError(f"Decryption failed for lock {lock_idx}")

    t1 = time.time()
    print(f"    Decrypted Lock {lock_idx + 1} in {t1 - t0:.2f}s: {m.hex()[:24]}...")
    return m

def main():
    enc_path = Path(__file__).resolve().parent.parent / "challenge" / "Fence" / "flag.enc"
    with open(enc_path) as f:
        data = json.load(f)

    hs = data["H"]
    cs = data["C"]
    r = data["R"]

    print(f"[*] Starting decryption of all {r} locks...")
    t_start = time.time()
    messages = []
    for idx in range(r):
        m = solve_lock(hs[idx], cs[idx], idx)
        messages.append(m)

    # Compute flag: XOR sum of all messages
    flag_len = len(messages[0])
    flag_bytes = bytearray(flag_len)
    for m in messages:
        for i in range(flag_len):
            flag_bytes[i] ^= m[i]

    flag_str = flag_bytes.decode(errors="replace")
    t_total = time.time() - t_start
    print(f"\n[+] All locks decrypted in {t_total:.2f}s!")
    print(f"[+] Flag bytes: {bytes(flag_bytes)}")
    print(f"[+] Flag: {flag_str}")

    # Save to flag.txt
    flag_file = Path(__file__).resolve().parent.parent / "flag.txt"
    with open(flag_file, "w") as f:
        f.write(flag_str.strip() + "\n")
    print(f"[+] Saved flag to {flag_file}")

if __name__ == "__main__":
    main()
