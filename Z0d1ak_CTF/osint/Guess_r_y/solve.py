#!/usr/bin/env python3
# Solution for: Guess r/y (osint)
import requests
import re

TARGET_URL = "https://geoint.z0d1ak.org"
session = requests.Session()

def solve():
    print(f"[*] Attacking: {TARGET_URL}")
    resp = session.get(TARGET_URL)
    print(f"[*] Status: {resp.status_code}")

    # TODO: Exploit logic here

if __name__ == '__main__':
    solve()
