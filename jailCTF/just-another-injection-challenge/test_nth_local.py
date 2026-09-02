import subprocess
import json

def run_jq(expr):
    cmd = ["jq", "-n", expr]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

print("Local Verification of nth Position Extraction:")

test_flag = "jail{flag_will_be_here_on_remote}"
# Let us test position 0, 1, 2, 4
for pos in [0, 1, 2, 4]:
    # jq filter: nth(pos; string | explode | tostream) | flatten | add
    # Note: nth(k; stream) yields the k-th item in stream!
    # stream elements are:
    # 0 -> [[0], 106] -> flatten|add is 106
    # 1 -> [[1], 97]  -> flatten|add is 98
    # 2 -> [[2], 105] -> flatten|add is 107
    rc, out, err = run_jq(f'"{test_flag}" | explode | [tostream] | .[{pos}] | flatten | add')
    print(f"Position {pos} (char '{test_flag[pos]}') -> sum: {out}")
