#!/usr/bin/env python3
# Solution for: Portalis (Web)
import requests
import re

TARGET_URL = "http://91.107.189.166:3000"
session = requests.Session()

def solve():
    print(f"[*] Attacking: {TARGET_URL}")
    resp = session.get(TARGET_URL)
    print(f"[*] Status: {resp.status_code}")

    # TODO: Exploit logic here

if __name__ == '__main__':
    solve()
