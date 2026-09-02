#!/usr/bin/env python3
# Solution for: Vivarium (crypto)
import requests
import re

TARGET_URL = "https://vivarium-lblgay6n.challenge.2026.haruulzangi.mn"
session = requests.Session()

def solve():
    print(f"[*] Attacking: {TARGET_URL}")
    resp = session.get(TARGET_URL)
    print(f"[*] Status: {resp.status_code}")

    # TODO: Exploit logic here

if __name__ == '__main__':
    solve()
