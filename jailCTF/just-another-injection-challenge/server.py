#!/usr/local/bin/python3
import subprocess

while expr := input("expr: ").strip():
    if any(c not in "|abcdefghijklmnopqrstuvwxyz" for c in expr):
        print("blocked")
        continue
    try:
        subprocess.run(["jq", "-n", expr], capture_output=True, timeout=2, check=True)
        print("ok")
    except:
        print("error")
