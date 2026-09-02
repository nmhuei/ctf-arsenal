#!/usr/bin/env python3
# Solution for: Moogle Arrived (Web)
import requests
import re

TARGET_URL = "http://13.203.69.239:31006/login"
session = requests.Session()

def solve():
    print(f"[*] Attacking: {TARGET_URL}")
    resp = session.get(TARGET_URL)
    print(f"[*] Status: {resp.status_code}")

    # TODO: Exploit logic here

if __name__ == '__main__':
    solve()
