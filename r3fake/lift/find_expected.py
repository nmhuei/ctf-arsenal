#!/usr/bin/env python3
"""
Analyze the binary to find the expected flag content values.
Look for patterns in the .eh_frame / .text sections that might
contain the 32 expected bytes for the flag content.
"""

import struct

BINARY_PATH = '/home/light/Workspace/CTF/r3fake/lift/chall'
FLAG_LEN = 39
CONTENT_LEN = 32

with open(BINARY_PATH, 'rb') as f:
    data = f.read()

# Search for "R3CTF{" to find where the prefix is stored
prefix_offset = data.find(b"R3CTF{")
print(f"'R3CTF{{' found at file offset: 0x{prefix_offset:x}")
print(f"Section: rodata (starts at 0x21f000)")

# Search for sets of 32 printable ASCII bytes
# These could be the expected flag content
print(f"\nSearching for 32-byte printable ASCII sequences...")
found = []
for i in range(len(data) - 32):
    chunk = data[i:i+32]
    if all(0x20 <= b <= 0x7e for b in chunk):
        found.append((i, chunk))

# Sort by uniqueness (looking for sequences that don't repeat)
if found:
    print(f"Found {len(found)} 32-byte printable sequences")
    # Show sequences in relevant sections
    for offset, chunk in found[:20]:
        print(f"  0x{offset:06x}: {chunk.decode('latin-1')}")
        if offset > 0x21f000 and offset < 0x2b8000:
            print(f"  *** In rodata/data section! ***")
        elif offset > 0x1100 and offset < 0x21ed4e:
            print(f"  *** In .text section! ***")
else:
    print("No exact 32-byte printable sequences found")

# Try XOR-encoded: search for non-printable sequences where XORing with a
# single key gives printable ASCII
print("\nSearching for XOR-encoded 32-byte sequences...")
for key in range(256):
    decoded = bytes(b ^ key for b in data[0x214326:0x214326+13*1024][:CONTENT_LEN])
    if all(0x20 <= b <= 0x7e for b in decoded):
        print(f"  XOR key 0x{key:02x}: {decoded.decode('latin-1')} (at validation func start)")

# Look in .eh_frame section for interesting patterns
# .eh_frame_hdr is at 0x21f02c, size 0x1e92c
# .eh_frame is at 0x23d958, size 0x7a490
print(f"\nExamining .eh_frame_hdr section (0x21f02c - 0x23d958)...")
eh_frame_hdr_offset = 0x21f000 + 0x02c  # Actually this is file offset too since LOAD=VA
eh_frame_hdr_start = 0x21f02c
eh_frame_hdr_end = 0x23d958

# Look for the tag pattern: 0x8000000000000000
print("\nSearching for tagged pointer pattern 0x8000...")
for i in range(len(data) - 8):
    val = struct.unpack('<Q', data[i:i+8])[0]
    if val & 0x8000000000000000 and (val & 0xFFFFFFFF) > 0x20000:
        # High bit set, likely a tagged pointer
        target = val & 0x7FFFFFFFFFFFFFFF
        if 0x211000 < target < 0x220000:  # In the validation function area
            print(f"  Found tagged pointer at 0x{i:x}: -> 0x{target:x}")

print("\nDone")
