def main():
    # Base 3, 4, 6 offsets for the 8 waves
    wave_offsets = [
        ((1, -3), (3, -1), (2, -2)), # Wave 1
        ((1, -3), (3, -1), (3, -1)), # Wave 2
        ((-3, 1), (2, 2),  (3, -1)), # Wave 3
        ((-2, 2), (2, 2),  (2, -2)), # Wave 4
        ((-3, -1),(3, -1), (2, -2)), # Wave 5
        ((-1, 3), (2, 2),  (2, -2)), # Wave 6
        ((1, 3),  (2, 2),  (3, 1)),  # Wave 7
        ((-3, 0), (3, 0),  (2, -2))  # Wave 8
    ]
    
    ccw_offsets = [
        (3, 0), (3, 1), (2, 2), (1, 3), (0, 3), (-1, 3), (-2, 2), (-3, 1),
        (-3, 0), (-3, -1), (-2, -2), (-1, -3), (0, -3), (1, -3), (2, -2), (3, -1)
    ]
    
    mappings = {
        "CCW_East": {off: i for i, off in enumerate(ccw_offsets)},
        "CW_East": {off: i for i, off in enumerate([ccw_offsets[0]] + ccw_offsets[1:][::-1])},
        "CCW_North": {off: i for i, off in enumerate(ccw_offsets[4:] + ccw_offsets[:4])},
        "CW_North": {
            (0, 3): 0, (-1, 3): 1, (-2, 2): 2, (-3, 1): 3, (-3, 0): 4, (-3, -1): 5, (-2, -2): 6, (-1, -3): 7,
            (0, -3): 8, (1, -3): 9, (2, -2): 10, (3, -1): 11, (3, 0): 12, (3, 1): 13, (2, 2): 14, (1, 3): 15
        }
    }
    
    for name, offset_map in mappings.items():
        print(f"\n--- Mapping: {name} ---")
        
        # We collect 12 bits per wave: (val3 << 8) | (val4 << 4) | val6
        vals = []
        for o3, o4, o6 in wave_offsets:
            v3 = offset_map[o3]
            v4 = offset_map[o4]
            v6 = offset_map[o6]
            vals.append((v3 << 8) | (v4 << 4) | v6)
            
        print(f"12-bit hex values: {[hex(v) for v in vals]}")
        
        # Pack into bitstream (big-endian bits)
        bitstream = ""
        for v in vals:
            bitstream += f"{v:012b}"
            
        # Convert bitstream to bytes
        bytes_list = []
        for i in range(0, len(bitstream), 8):
            b_str = bitstream[i:i+8]
            if len(b_str) == 8:
                bytes_list.append(int(b_str, 2))
                
        print(f"Decoded bytes: {[hex(b) for b in bytes_list]}")
        # Print ASCII
        ascii_chars = []
        for b in bytes_list:
            if 32 <= b <= 126:
                ascii_chars.append(chr(b))
            else:
                ascii_chars.append('.')
        print(f"ASCII: {''.join(ascii_chars)}")

if __name__ == '__main__':
    main()
