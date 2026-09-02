#!/usr/bin/env python3
# Solution for: Signal Race (Pwnable)
from pwn import *

HOST = '91.107.187.160'
PORT = 18121

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
