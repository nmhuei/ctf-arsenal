import os
import subprocess
import re

solvers = [
    "cryptohack_challenges/ctf-archive/ctf-archive-2021/chaos-zh3r0-ctf-v2/solve/solve.py",
    "cryptohack_challenges/ctf-archive/ctf-archive-2021/a-joke-cipher-hkcert-ctf/solve/solve.py",
    "cryptohack_challenges/ctf-archive/ctf-archive-2021/1n_jection-zh3r0-ctf-v2/solve/solve.py",
    "cryptohack_challenges/ctf-archive/ctf-archive-2021/1337crypt-v2-downunderctf/solve/solve.py",
    "cryptohack_challenges/zkp/zkp-challenges/couples/solve/solve.py",
    "cryptohack_challenges/ctf-archive/ctf-archive-2020/2020-tetctf/solve/solve.py"
]

python_bin = os.path.abspath(".venv/bin/python")

for s in solvers:
    d = os.path.dirname(s)
    f = os.path.basename(s)
    print(f"Running {s}...")
    try:
        out = subprocess.check_output([python_bin, f], cwd=d, stderr=subprocess.STDOUT, timeout=60).decode()
        match = re.search(r"(\w+\{.*?\})", out)
        if match:
            print("Flag:", match.group(1))
        else:
            print("No flag found in output")
    except Exception as e:
        print("Failed:", e)
