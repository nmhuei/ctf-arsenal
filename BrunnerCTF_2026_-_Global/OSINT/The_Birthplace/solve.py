#!/usr/bin/env python3
# Solution for: The Birthplace (OSINT)
import requests
import re

TARGET_URL = "https://what3words.com"
session = requests.Session()

def solve():
    print(f"[*] Attacking: {TARGET_URL}")
    resp = session.get(TARGET_URL)
    print(f"[*] Status: {resp.status_code}")

    # TODO: Exploit logic here

if __name__ == '__main__':
    solve()
