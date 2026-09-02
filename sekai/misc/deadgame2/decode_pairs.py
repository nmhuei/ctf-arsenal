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
    
    ccw_offsets = [
        (3, 0), (3, 1), (2, 2), (1, 3), (0, 3), (-1, 3), (-2, 2), (-3, 1),
        (-3, 0), (-3, -1), (-2, -2), (-1, -3), (0, -3), (1, -3), (2, -2), (3, -1)
    ]
    
    mappings = {
        "CCW_East": {off: i for i, off in enumerate(ccw_offsets)},
        "CW_East": {off: i for i, off in enumerate([ccw_offsets[0]] + ccw_offsets[1:][::-1])},
        "CCW_North": {off: i for i, off in enumerate(ccw_offsets[4:] + ccw_offsets[:4])},
        "CW_North": {off: i for i, off in enumerate([ccw_offsets[4]] + ccw_offsets[5:][::-1] + ccw_offsets[:4][::-1])}
    }
    
    # Let's fix CW_North mapping properly:
    # 0: (0, 3), 15: (1, 3), 14: (2, 2), 13: (3, 1), 12: (3, 0), 11: (3, -1), 10: (2, -2), 9: (1, -3)
    # 8: (0, -3), 7: (-1, -3), 6: (-2, -2), 5: (-3, -1), 4: (-3, 0), 3: (-3, 1), 2: (-2, 2), 1: (-1, 3)
    cw_north_map = {
        (0, 3): 0, (-1, 3): 1, (-2, 2): 2, (-3, 1): 3, (-3, 0): 4, (-3, -1): 5, (-2, -2): 6, (-1, -3): 7,
        (0, -3): 8, (1, -3): 9, (2, -2): 10, (3, -1): 11, (3, 0): 12, (3, 1): 13, (2, 2): 14, (1, 3): 15
    }
    mappings["CW_North"] = cw_north_map

    for name, offset_map in mappings.items():
        print(f"\n--- Mapping: {name} ---")
        hex_digits = []
        bytes_list = []
        for off3, off4 in pairs:
            val3 = offset_map.get(off3, None)
            val4 = offset_map.get(off4, None)
            if val3 is not None and val4 is not None:
                b = (val3 << 4) | val4
                hex_digits.append(f"{b:02x}")
                bytes_list.append(b)
            else:
                hex_digits.append("??")
                bytes_list.append(None)
                
        print(f"Hex: {' '.join(hex_digits)}")
        ascii_chars = []
        for b in bytes_list:
            if b is None:
                ascii_chars.append('?')
            elif 32 <= b <= 126:
                ascii_chars.append(chr(b))
            else:
                ascii_chars.append('.')
        print(f"ASCII: {''.join(ascii_chars)}")

if __name__ == '__main__':
    main()
