import json
import subprocess
import re
import sys
import time

def solve_one_h(h, n=128, q=268435361):
    # Build circulant matrix for h mod (X^n + 1)
    # pm(a, b): row vector a * H = b
    # row i of H is X^i * h mod (X^n + 1)
    H_rows = []
    # X^0 * h = h
    cur = list(h)
    H_rows.append(cur)
    for i in range(1, n):
        # cur = X * cur mod (X^n + 1)
        # cur[0]*X + cur[1]*X^2 + ... + cur[n-1]*X^n
        # = -cur[n-1] + cur[0]*X + ... + cur[n-2]*X^{n-1}
        nxt = [(-cur[-1]) % q] + cur[:-1]
        H_rows.append(nxt)
        cur = nxt

    # Lattice basis (rows):
    # Top n rows: q * I_n, 0_n
    # Bottom n rows: H, I_n
    # A vector in lattice is (k * q + a * H, a) = (b, a)
    matrix_rows = []
    for i in range(n):
        row = [0] * (2 * n)
        row[i] = q
        matrix_rows.append(row)
    for i in range(n):
        row = list(H_rows[i]) + [0] * n
        row[n + i] = 1
        matrix_rows.append(row)

    # Format for flatter: "[ [ ... ] [ ... ] ]"
    lines = []
    lines.append("[")
    for r in matrix_rows:
        lines.append("[" + " ".join(map(str, r)) + "]")
    lines.append("]")
    matrix_str = "\n".join(lines)

    t0 = time.time()
    p = subprocess.run(["flatter"], input=matrix_str, text=True, capture_output=True)
    t1 = time.time()
    print(f"Flatter finished in {t1 - t0:.2f}s, exit code {p.returncode}")
    if p.returncode != 0:
        print("Flatter error:", p.stderr)
        return None

    # Parse output matrix
    out = p.stdout.strip()
    # Flatten numbers
    nums = list(map(int, re.findall(r'-?\d+', out)))
    if len(nums) != (2 * n) * (2 * n):
        print(f"Unexpected number of integers: {len(nums)} vs {(2*n)*(2*n)}")
        return None

    # Inspect first few rows
    for row_idx in range(5):
        row = nums[row_idx * 2 * n : (row_idx + 1) * 2 * n]
        norm_sq = sum(x**2 for x in row)
        b_part = row[:n]
        a_part = row[n:]
        print(f"Row {row_idx}: norm_sq = {norm_sq}, norm = {norm_sq**0.5:.2f}")
        print(f"  b non-zeros: {sum(1 for x in b_part if x != 0)}, set(b): {set(b_part)}")
        print(f"  a non-zeros: {sum(1 for x in a_part if x != 0)}, set(a): {set(a_part)}")

if __name__ == "__main__":
    with open("challenge/Fence/flag.enc") as f:
        data = json.load(f)
    print("Testing H[0]...")
    solve_one_h(data["H"][0], data["N"], data["Q"])
