#!/usr/bin/python3
import tempfile
import subprocess
import os


MEWLIX_YAML = """
name: no-name 
description: ''
mode: node
entrypoint: main
port: auto
source-files:
- src/**/*.mews
assets: []
flags: []
"""

inp = input("> ")

if any(c in 'mew = "(_^OwO^_).[_^UwU^_]"' for c in inp) or max(inp) > "~meow~":
    print('cats, unlimited cats, but no cats.')
    exit(1)

print('running')

with tempfile.TemporaryDirectory() as f:
    os.mkdir(os.path.join(f, "src"))
    with open(os.path.join(f, "src", "main.mews"), 'w') as f2:
        f2.write(inp)
    with open(os.path.join(f, "mewlix.yaml"), 'w') as f2:
        f2.write(MEWLIX_YAML)
    subprocess.run(["/app/mewlix", "run"], cwd=f)

print('goodbye')

