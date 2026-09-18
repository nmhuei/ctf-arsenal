#!/usr/bin/env python3
# Solution for: Mario (Crypto)
import argparse
from Crypto.Util.number import *
import hashlib

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='Optional remote URL adapter')
    parser.add_argument('--remote', metavar='HOST:PORT', help='Optional remote TCP adapter')
    return parser.parse_args()

def solve(options):
    # TODO: Crypto math / decryption logic here
    pass

if __name__ == '__main__':
    solve(parse_args())
