#!/usr/bin/env python3
# Solution for: w4nn4d13's Trap (Boot2root)
import requests
import re

TARGET_URL = "https://tryhackme.com/jr/ex0rcists"
session = requests.Session()

def solve():
    print(f"[*] Attacking: {TARGET_URL}")
    resp = session.get(TARGET_URL)
    print(f"[*] Status: {resp.status_code}")

    # TODO: Exploit logic here

if __name__ == '__main__':
    solve()
