#!/usr/bin/env python3
"""
Parse the validation function (0x214326) and extract all
data addresses it references via LEA instructions.
Then dump those data regions to find the comparison table.
"""

import struct
import sys

BINARY_PATH = '/home/light/Workspace/CTF/r3fake/lift/chall'

with open(BINARY_PATH, 'rb') as f:
    data = f.read()

# Validation function: file offset = VA since LOAD segment starts at 0
fcn_start = 0x214326
fcn_size = 0x3400  # ~13KB

fcn_data = data[fcn_start:fcn_start + fcn_size]

# Find LEA r/m64 instructions (RIP-relative)
# Pattern: 48 8d 05/15/1d/25/2d/35/3d XX XX XX XX (7 bytes)
# 48 8d 05 = lea rax, [rip+disp32]
# 48 8d 15 = lea rdx, [rip+disp32]
# 48 8d 1d = lea rbx, [rip+disp32]
# 48 8d 25 = lea rsp, [rip+disp32] (unlikely)
# 48 8d 2d = lea rbp, [rip+disp32]
# 48 8d 35 = lea rsi, [rip+disp32]
# 48 8d 3d = lea rdi, [rip+disp32]
# 48 8d 8d/95/9d/a5/ad/b5/bd = lea rXX, [rbp+disp32] (NOT rip-relative)

# Also 4c 8d 05/0d/15/1d/25/2d/35/3d = lea r8-r15, [rip+disp32]

references = []

for i in range(0, len(fcn_data) - 7):
    # Check for lea r64, [rip+disp32]
    byte0 = fcn_data[i]
    byte1 = fcn_data[i+1]

    if byte0 == 0x48:  # REX.W
        if byte1 in [0x05, 0x0d, 0x15, 0x1d, 0x25, 0x2d, 0x35, 0x3d]:
            # 48 8d XX = lea r64, [rip+disp32]
            if fcn_data[i+2] == 0x8d:  # This is actually wrong format, let me recheck
                pass

        # Correct format: 48 8d ?5 = lea rXX, [rip+disp32]
        # ?5 means mod=00, rm=101 (RIP-relative) when modrm byte is XX XXX 101
        # Let me just check second byte
        if byte1 == 0x8d and (fcn_data[min(i+3, len(fcn_data)-1)] & 0x07) == 0x05:
            # This is lea. Now check if it's RIP-relative
            modrm = fcn_data[i+2]
            mod = (modrm >> 6) & 0x03
            rm = modrm & 0x07

            if mod == 0 and rm == 5:  # RIP-relative
                disp = struct.unpack('<i', fcn_data[i+3:i+7])[0]
                instr_addr = fcn_start + i
                target_addr = instr_addr + 7 + disp  # addr after instruction + displacement
                reg_name = ['rax', 'rcx', 'rdx', 'rbx', 'rsp', 'rbp', 'rsi', 'rdi'][(modrm >> 3) & 0x07]

                references.append({
                    'instr_addr': instr_addr,
                    'target_addr': target_addr,
                    'reg': reg_name,
                    'disp': disp,
                })

print(f"Found {len(references)} RIP-relative LEA instructions in validation function")
print()

# Also check with REX.W prefix variants
for prefix in [0x48, 0x4c]:  # REX.W and REX.WR
    for i in range(0, len(fcn_data) - 7):
        if fcn_data[i] == prefix and fcn_data[i+1] == 0x8d:
            modrm = fcn_data[i+2]
            mod = (modrm >> 6) & 0x03
            rm = modrm & 0x07

            if mod == 0 and rm == 5:  # RIP-relative
                # But this addr is already checked for 0x48 from the first loop
                # Skip duplicates
                instr_addr = fcn_start + i
                if any(r['instr_addr'] == instr_addr for r in references):
                    continue

                disp = struct.unpack('<i', data[fcn_start+i+3:fcn_start+i+7])[0]
                target_addr = instr_addr + 7 + disp

                reg_idx = (modrm >> 3) & 0x07
                if prefix == 0x48:
                    reg_name = ['rax', 'rcx', 'rdx', 'rbx', 'rsp', 'rbp', 'rsi', 'rdi'][reg_idx]
                else:  # 0x4c
                    reg_name = f'r{8 + reg_idx}'

                references.append({
                    'instr_addr': instr_addr,
                    'target_addr': target_addr,
                    'reg': reg_name,
                    'disp': disp,
                })

print(f"After full scan: {len(references)} RIP-relative LEA instructions")
print()

# Sort by target address
references.sort(key=lambda r: r['target_addr'])

# Dump each unique reference target
seen_addrs = set()
for ref in references:
    if ref['target_addr'] in seen_addrs:
        continue
    seen_addrs.add(ref['target_addr'])

    ta = ref['target_addr']
    # Check if it's in the binary's mapped range
    if ta >= 0x1100 and ta < 0x2b9100:
        # Print some bytes at this address
        offset = ta  # file offset = VA
        size = min(32, len(data) - offset)
        if size < 4:
            continue
        raw = data[offset:offset+size]

        # Try to interpret as string
        try:
            s = raw.decode('latin-1')
            printable = all(0x20 <= ord(c) <= 0x7e or c in '\n\r\t' for c in s)
            as_str = f"  -> '{s}'" if printable else f"  -> hex: {raw[:16].hex()}"
        except:
            as_str = f"  -> hex: {raw[:16].hex()}"

        # Check if this looks like a pointer
        if size >= 8:
            val = struct.unpack('<Q', raw[:8])[0]
            if 0x1100 < val < 0x2b9100:
                as_str += f" (pointer to 0x{val:x})"

        print(f"0x{ref['instr_addr']:05x} -> 0x{ta:06x} [{ref['reg']}]: {as_str}")

# Look specifically for data in the .text section (not in the function itself)
print("\n=== Data references in .text section (outside validation function) ===")
for ref in references:
    ta = ref['target_addr']
    if ta >= 0x1100 and ta < fcn_start:
        offset = ta
        raw = data[offset:offset+16]
        print(f"0x{ta:06x}: {raw.hex()}")

# Now let's also search for the pattern: mov byte [reg+offset], constant or cmp byte [reg+offset], constant
# These would be the actual comparison instructions
print("\n=== Looking for direct comparison patterns ===")
for i in range(0, len(fcn_data) - 4):
    # cmp byte [reg+X], imm8
    # Pattern: 80 7? XX YY where YY is the immediate
    if fcn_data[i] == 0x80 and (fcn_data[i+1] & 0xFF) == 0x7f:
        # cmp byte [rdi+disp8], imm8
        offset = struct.unpack('<b', bytes([fcn_data[i+2]]))[0]
        imm = fcn_data[i+3]
        instr_addr = fcn_start + i
        if 0x20 <= imm <= 0x7e:
            print(f"  0x{instr_addr:05x}: cmp byte [rdi{offset:+d}], '{chr(imm)}' (0x{imm:02x})")
