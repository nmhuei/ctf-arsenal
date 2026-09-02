#!/usr/bin/env python3
# Solution for: TurboCalc (Pwn)
from pwn import *

HOST = '13.203.69.239'
PORT = 31004

context.log_level = 'debug'
# context.arch = 'amd64'
# context.terminal = ['tmux', 'splitw', '-h']

def solve():
    if args.REMOTE:
        r = remote(HOST, PORT)
    else:
        # r = process('./vuln')
        r = remote(HOST, PORT)

    # TODO: Exploit logic here
    # r.sendlineafter(b'> ', b'payload')

    r.interactive()

if __name__ == '__main__':
    solve()
