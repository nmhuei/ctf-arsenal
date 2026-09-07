#!/usr/bin/env python3
# Solution for: You would never hack a CTF (boot2root)
import requests
import re

TARGET_URL = "https://media1.tenor.com/m/ZYE3KzTM4acAAAAd/piracy-its-a-crime-you-wouldnt-steal-a-car.gif)"
session = requests.Session()

def solve():
    print(f"[*] Attacking: {TARGET_URL}")
    resp = session.get(TARGET_URL)
    print(f"[*] Status: {resp.status_code}")

    # TODO: Exploit logic here

if __name__ == '__main__':
    solve()
