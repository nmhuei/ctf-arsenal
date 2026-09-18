#!/usr/bin/env python3
# Solution for: 🎟 The Lottery Race (Web)
import argparse
import requests
import re

LOCAL_URL = "http://127.0.0.1:8000"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='Remote URL; omitted means the local harness')
    parser.add_argument('--remote', metavar='HOST:PORT', help='Optional TCP adapter')
    return parser.parse_args()

def solve(options):
    target_url = options.url or LOCAL_URL
    session = requests.Session()
    print(f"[*] Testing: {target_url}")
    resp = session.get(target_url)
    print(f"[*] Status: {resp.status_code}")

    # TODO: Exploit logic here

if __name__ == '__main__':
    solve(parse_args())
