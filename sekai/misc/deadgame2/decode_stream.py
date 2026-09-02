import sc2reader
import math

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    probes = [ev for ev in events if ev.__class__.__name__ == 'UnitBornEvent' and ev.control_pid == 2 and ev.unit_type_name == 'Probe']
    probes.sort(key=lambda x: x.frame)
    probes = [p for p in probes if p.frame > 0]
    
    nexus_coords = {
        0: (201, 56), 1: (177, 56), 2: (201, 78), 3: (110, 71),
        4: (91, 71), 5: (60, 78), 6: (59, 94)
    }

    def get_base_id(x, y):
        if x > 195 and y < 65:
            return 0
        elif 170 <= x <= 190 and y < 65:
            return 1
        elif x > 195 and 75 <= y <= 85:
            return 2
        elif 100 <= x <= 120 and 65 <= y <= 75:
            return 3
        elif 90 <= x < 100 and 65 <= y <= 75:
            return 4
        elif 60 <= x <= 70 and 75 <= y <= 85:
            return 5
        elif 60 <= x <= 70 and y >= 90:
            return 6
        else:
            return -1

    offsets = []
    for p in probes:
        bid = get_base_id(p.x, p.y)
        if bid != -1:
            nx, ny = nexus_coords[bid]
            offsets.append((p.x - nx, p.y - ny))
            
    # The 16 possible offsets ordered counter-clockwise starting from (3, 0) (East)
    ccw_offsets = [
        (3, 0),   # 0.0
        (3, 1),   # 18.4
        (2, 2),   # 45.0
        (1, 3),   # 71.6
        (0, 3),   # 90.0
        (-1, 3),  # 108.4
        (-2, 2),  # 135.0
        (-3, 1),  # 161.6
        (-3, 0),  # 180.0
        (-3, -1), # 198.4
        (-2, -2), # 225.0
        (-1, -3), # 251.6 (unused)
        (0, -3),  # 270.0
        (1, -3),  # 288.4
        (2, -2),  # 315.0
        (3, -1)   # 341.6
    ]
    
    # Let's generate mapping dictionaries for:
    # 1. CCW starting from East (0)
    # 2. CW starting from East (0)
    # 3. CCW starting from North (0)
    # 4. CW starting from North (0)
    
    def try_decode(offset_map, name):
        hex_digits = []
        for off in offsets:
            if off in offset_map:
                hex_digits.append(f"{offset_map[off]:x}")
            else:
                hex_digits.append("?")
        
        # Group into bytes
        hex_str = "".join(hex_digits)
        print(f"\n--- Mapping: {name} ---")
        print(f"Hex stream: {hex_str[:80]}...")
        
        # Decode bytes
        bytes_list = []
        for i in range(0, len(hex_str), 2):
            b_str = hex_str[i:i+2]
            if '?' in b_str:
                bytes_list.append(ord('?'))
            else:
                bytes_list.append(int(b_str, 16))
                
        # Print printable ASCII
        ascii_chars = []
        for b in bytes_list:
            if 32 <= b <= 126:
                ascii_chars.append(chr(b))
            else:
                ascii_chars.append('.')
        print(f"ASCII: {''.join(ascii_chars)}")

    # 1. CCW from East
    map_ccw_east = {off: i for i, off in enumerate(ccw_offsets)}
    try_decode(map_ccw_east, "CCW starting from East")
    
    # 2. CW from East
    cw_offsets = [ccw_offsets[0]] + ccw_offsets[1:][::-1]
    map_cw_east = {off: i for i, off in enumerate(cw_offsets)}
    try_decode(map_cw_east, "CW starting from East")
    
    # 3. CCW from North
    # (0, 3) is index 4 in ccw_offsets
    ccw_north = ccw_offsets[4:] + ccw_offsets[:4]
    map_ccw_north = {off: i for i, off in enumerate(ccw_north)}
    try_decode(map_ccw_north, "CCW starting from North")
    
    # 4. CW from North
    cw_north = [ccw_north[0]] + ccw_north[1:][::-1]
    map_cw_north = {off: i for i, off in enumerate(cw_north)}
    try_decode(map_cw_north, "CW starting from North")

if __name__ == '__main__':
    main()
