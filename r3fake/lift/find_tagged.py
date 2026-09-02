#!/usr/bin/env python3
"""
Search for tagged pointers in the validation function that encode
expected byte values for comparison.
Tagged pointer with high bit set: 0x80000000000000XX where XX is expected byte.
"""

import struct

BINARY_PATH = '/home/light/Workspace/CTF/r3fake/lift/chall'
CONTENT_LEN = 32

with open(BINARY_PATH, 'rb') as f:
    data = f.read()

FLAG_PREFIX = b"R3CTF{"

# Search for tagged pointers with high bit set and small values
# Pattern: 48 B8 + 8 bytes (movabs rax, imm64) where imm64 has high bit set and small lower bits
# Or: 48 09 D0 (or rax, rdx) which is used to tag a pointer

# Let's search for the MOVABS that creates tagged pointers
# 48 B8 XX XX XX XX XX XX XX XX = movabs rax, 0xXXXXXXXXXXXXXX
# Where the value has bit 63 set (0x80...) and bits 0-7 are a small value
print("Searching for tagged pointer constants in validation function (0x214326-0x217500):")
fcn_start = 0x214326
fcn_end = 0x217500

# Approach: scan for movabs rax with 0x8000000000000000 pattern
expected_bytes = [None] * CONTENT_LEN

for i in range(fcn_start, fcn_end - 8):
    if data[i] == 0x48 and data[i+1] == 0xb8:
        # movabs rax, imm64
        val = struct.unpack('<Q', data[i+2:i+10])[0]
        if val & 0x8000000000000000:  # High bit set
            lower = val & 0x7FFFFFFFFFFFFFFF
            # Check if lower looks like a printable ASCII value (or at least < 256)
            if lower < 256 and 0x20 <= lower <= 0x7e:
                print(f"  0x{i:x}: movabs rax, 0x{val:016x} -> expected byte '{chr(lower)}' (0x{lower:02x})")
                # Find which character position this corresponds to
                # (scan backward for LEA that loaded a position-specific address)
                for j in range(max(fcn_start, i-100), i):
                    if data[j] == 0xba and j > fcn_start + 0x100:  # mov edx/rdx, imm? No this is wrong
                        pass

# Also search for `or rax, rdx` which is used to set the tag bit
# Pattern: 48 09 D0 = or rax, rdx (setting high bit from rdx to rax)
print("\nSearching for OR tagging pattern (or rax, rdx, or rax, rdi)...")
tagged_values = []

for i in range(fcn_start, fcn_end - 3):
    # Look for `movabs rax, VAL; or rdx/rdi, rax` pattern
    if data[i] == 0x48 and data[i+1] == 0xb8:
        val = struct.unpack('<Q', data[i+2:i+10])[0]
        if val == 0x8000000000000000:
            # Check if next instruction sets rdx/rdi to something and then ORs
            # The tag pattern is:
            # lea rdx, [addr]     or    movabs rax, 0x8000...
            # movabs rax, 0x8000...      lea rdx, [addr]
            # or rax, rdx               or rax, rdx
            after = i + 10
            if after + 4 < fcn_end:
                if data[after] == 0x48 and data[after+1] == 0x09 and data[after+2] == 0xd0:
                    # or rax, rdx - rdx was set before with lea
                    # Find the LEA:
                    for j in range(max(fcn_start, after-20), after):
                        if data[j] == 0x48 and data[j+1] in [0x8d, 0x8b, 0xba]:
                            # lea rdx, [...] or similar
                            pass
                    tagged_values.append((i, val, after))

# Actually, let me look at the data references from the validation function
# The tagged pointers might NOT be created by MOVABS but by LEA+OR
# LEA loads an address into rdx, then OR with rax (which has 0x8000...)
# The address IS the expected value or a reference

# Let me search for the pattern differently:
# 1. Find all LEA rdx, [rip+disp] in validation function
# 2. The target address might contain comparison-related data

print("\nChecking data at LEA-referenced addresses (extracting embedded bytes):")

# Let me look at the actual bytes at the referenced addresses
# From the earlier analysis, the LEA targets are functions starting with 0x55 (push rbp)
# But within those functions, there might be embedded data

# Look at one of the short Type B functions to find comparison constants
for func_addr in [0xdde9b, 0xdddd2, 0xde024, 0xde046, 0xde012]:
    raw = data[func_addr:func_addr+50]
    print(f"\nFunction at 0x{func_addr:05x}:")
    for k in range(0, len(raw), 8):
        chunk = raw[k:k+8]
        val = struct.unpack('<Q', chunk.ljust(8, b'\x00'))[0]
        hexstr = chunk.hex()
        ascii_str = ''.join(chr(b) if 0x20 <= b <= 0x7e else '.' for b in chunk)
        print(f"  0x{func_addr+k:05x}: {hexstr:16s} | {ascii_str} | val=0x{val:016x}")

# Extract all embedded data in the .text section that looks like expected flag values
print(f"\nSearching for 32-byte sequences in .text section that are the flag content...")

# The flag content should be printable ASCII, stored consecutively somewhere
for search_start in [0xd0000, 0xd5000, 0xe0000, 0xe5000, 0x210000, 0x214000]:
    end = min(search_start + 0x10000, len(data))
    region = data[search_start:end]
    for k in range(len(region) - CONTENT_LEN):
        chunk = region[k:k+CONTENT_LEN]
        if all(0x20 <= b <= 0x7e for b in chunk):
            s = chunk.decode('ascii')
            if len(set(s)) > 10:  # More than 10 unique chars = likely meaningful
                print(f"  0x{search_start+k:06x}: {s}")

print("\nDone")
