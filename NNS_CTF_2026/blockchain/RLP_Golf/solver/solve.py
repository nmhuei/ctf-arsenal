#!/usr/bin/env python3
# Solution for: RLP Golf (blockchain)
import requests
import re

TARGET_URL = "https://ethereum.org/developers/docs/data-structures-and-encoding/rlp/)"
session = requests.Session()

def solve():
    print(f"[*] Attacking: {TARGET_URL}")
    resp = session.get(TARGET_URL)
    print(f"[*] Status: {resp.status_code}")

    # TODO: Exploit logic here

if __name__ == '__main__':
    solve()
