#!/usr/bin/env python3
# Solution for: NBT Needle (MISC)
import requests
import re

TARGET_URL = "https://minecraft.fandom.com/wiki/NBT_format)"
session = requests.Session()

def solve():
    print(f"[*] Attacking: {TARGET_URL}")
    resp = session.get(TARGET_URL)
    print(f"[*] Status: {resp.status_code}")

    # TODO: Exploit logic here

if __name__ == '__main__':
    solve()
