#!/usr/bin/env python3
# Solution for: A Star Trail 1 (Misc)
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='Optional remote URL adapter')
    parser.add_argument('--remote', metavar='HOST:PORT', help='Optional remote TCP adapter')
    return parser.parse_args()

def solve(options):
    # TODO: Solution script
    print("[*] Solving A Star Trail 1...")

if __name__ == '__main__':
    solve(parse_args())
