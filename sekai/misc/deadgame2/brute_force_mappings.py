def main():
    # Base 3 & Base 4 offsets for the 8 waves
    pairs = [
        ((1, -3), (3, -1)),  # Wave 1
        ((1, -3), (3, -1)),  # Wave 2
        ((-3, 1), (2, 2)),   # Wave 3
        ((-2, 2), (2, 2)),   # Wave 4
        ((-3, -1), (3, -1)), # Wave 5
        ((-1, 3), (2, 2)),   # Wave 6
        ((1, 3), (2, 2)),    # Wave 7
        ((-3, 0), (3, 0))    # Wave 8
    ]
    
    # 16 offsets in CCW order around the circle starting from (3, 0)
    ccw_offsets = [
        (3, 0), (3, 1), (2, 2), (1, 3), (0, 3), (-1, 3), (-2, 2), (-3, 1),
        (-3, 0), (-3, -1), (-2, -2), (-1, -3), (0, -3), (1, -3), (2, -2), (3, -1)
    ]
    
    # Generate all 16 shifts for CCW
    all_mappings = []
    for shift in range(16):
        offsets_shifted = ccw_offsets[shift:] + ccw_offsets[:shift]
        all_mappings.append((f"CCW_shift_{shift}", {off: i for i, off in enumerate(offsets_shifted)}))
        
    # Generate all 16 shifts for CW (reverse of CCW)
    cw_offsets = [ccw_offsets[0]] + ccw_offsets[1:][::-1]
    for shift in range(16):
        offsets_shifted = cw_offsets[shift:] + cw_offsets[:shift]
        all_mappings.append((f"CW_shift_{shift}", {off: i for i, off in enumerate(offsets_shifted)}))
        
    for name, offset_map in all_mappings:
        bytes_list = []
        for off3, off4 in pairs:
            val3 = offset_map.get(off3, None)
            val4 = offset_map.get(off4, None)
            if val3 is not None and val4 is not None:
                b = (val3 << 4) | val4
                # Clear MSB
                b = b & 0x7f
                bytes_list.append(b)
            else:
                bytes_list.append(None)
                
        # Format as string
        chars = []
        for b in bytes_list:
            if b is None:
                chars.append('?')
            elif 32 <= b <= 126:
                chars.append(chr(b))
            else:
                chars.append('.')
        decoded = "".join(chars)
        
        # We only print if there's at least 3 printable ASCII alphanumeric/underscore chars
        alnum_count = sum(1 for c in decoded if c.isalnum() or c == '_')
        if alnum_count >= 3:
            print(f"{name:15s} | Hex: {' '.join(f'{b:02x}' if b is not None else '??' for b in bytes_list)} | ASCII: {decoded}")

if __name__ == '__main__':
    main()
