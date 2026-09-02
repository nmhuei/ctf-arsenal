#!/usr/bin/env python3
from pwn import *
import subprocess
import os

HOST = "mikuprotect.chals.sekai.team"
PORT = 1337

context.log_level = 'debug'

def solve_pow(challenge):
    result = subprocess.run(
        challenge,
        shell=True,
        capture_output=True,
        text=True,
        timeout=60
    )
    return result.stdout.strip()

r = remote(HOST, PORT)

# Read PoW
pow_line = r.recvline().decode()
print(f"PoW: {pow_line}")
cmd_line = r.recvline().decode().strip()
print(f"CMD: {cmd_line}")

sol = solve_pow(cmd_line)
print(f"SOL: {sol}")

r.sendline(sol.encode())

# Now read protocol
for i in range(50):
    try:
        line = r.recvline(timeout=5)
        print(f"LINE: {line}")
    except:
        print("TIMEOUT")
        break

r.close()
