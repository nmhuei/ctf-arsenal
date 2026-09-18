#!/usr/bin/env python3
# Solution for: Mic Check (Baby 👶)
import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser(description="Solver for Mic Check (ASIS CTF Quals 2026)")
    parser.add_argument('--url', help='Optional remote URL adapter')
    parser.add_argument('--remote', metavar='HOST:PORT', help='Optional remote TCP adapter')
    return parser.parse_args()

def solve(options):
    print("[*] Solving Mic Check...")

    # Challenge presents 5 vintage 7/14-segment LED display blocks in ASCII art:
    # [1] f4r3w3ll
    # [2] cl4ss1c
    # [3] h3ll0
    # [4] unc3rt41n (taking into account drifted top-row spacing in ASCII rendering)
    # [5] 3r4!
    words = [
        "f4r3w3ll",
        "cl4ss1c",
        "h3ll0",
        "unc3rt41n",
        "3r4!"
    ]

    flag = f"ASIS{'{'}{'_'.join(words)}{'}'}"
    print(f"[+] Found flag: {flag}")

    flag_path = os.path.join(os.path.dirname(__file__), "flag.txt")
    with open(flag_path, "w") as f:
        f.write(flag + "\n")
    print(f"[+] Flag saved to {flag_path}")

    # Also save flag in the challenge root directory
    chall_flag_path = os.path.join(os.path.dirname(__file__), "..", "flag.txt")
    with open(chall_flag_path, "w") as f:
        f.write(flag + "\n")

    return flag

if __name__ == '__main__':
    solve(parse_args())
