#!/usr/bin/env python3
# Solution for: Mousa (Reverse)
import argparse
from pwn import *

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 1337

context.log_level = 'debug'
# context.arch = 'amd64'
# context.terminal = ['tmux', 'splitw', '-h']

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--remote', metavar='HOST:PORT', help='Connect to a remote service')
    parser.add_argument('--url', help='Optional URL adapter for HTTP-based variants')
    return parser.parse_args()

def solve(options):
    if options.remote:
        host, port = options.remote.rsplit(':', 1)
        r = remote(host, int(port))
    else:
        # Local-first: replace with the local binary or harness command.
        r = process('./vuln')

    # TODO: Exploit logic here
    # r.sendlineafter(b'> ', b'payload')

    r.interactive()

if __name__ == '__main__':
    solve(parse_args())
