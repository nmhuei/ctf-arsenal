import sc2reader

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

    # Reconstruct waves with gap <= 150
    waves = []
    current_wave = []
    for p in probes:
        if not current_wave:
            current_wave.append(p)
        else:
            if p.frame - current_wave[-1].frame <= 150:
                current_wave.append(p)
            else:
                waves.append(current_wave)
                current_wave = [p]
    if current_wave:
        waves.append(current_wave)
        
    ccw_offsets = [
        (3, 0), (3, 1), (2, 2), (1, 3), (0, 3), (-1, 3), (-2, 2), (-3, 1),
        (-3, 0), (-3, -1), (-2, -2), (-1, -3), (0, -3), (1, -3), (2, -2), (3, -1)
    ]
    
    # 4 mappings
    mappings = {
        "CCW_East": {off: i for i, off in enumerate(ccw_offsets)},
        "CW_East": {off: i for i, off in enumerate([ccw_offsets[0]] + ccw_offsets[1:][::-1])},
        "CCW_North": {off: i for i, off in enumerate(ccw_offsets[4:] + ccw_offsets[:4])},
        "CW_North": {off: i for i, off in enumerate([ccw_offsets[4]] + ccw_offsets[5:][::-1] + ccw_offsets[:4][::-1])} # Wait, CW North needs careful reverse
    }
    
    # Correct CW_North:
    cw_north_offsets = [
        (0, 3), (-1, 3), (-2, 2), (-3, 1), (-3, 0), (-3, -1), (-2, -2), (-1, -3),
        (0, -3), (1, -3), (2, -2), (3, -1), (3, 0), (3, 1), (2, 2), (1, 3)
    ]
    # CW is reverse of CCW:
    # CCW: North, NNW, NW, WNW, W, WSW, SW, SSW, S, SSE, SE, ESE, E, ENE, NE, NNE
    # Let's write them down:
    # 0: North (0, 3)
    # 1: NNE (1, 3)
    # 2: NE (2, 2)
    # 3: ENE (3, 1)
    # 4: E (3, 0)
    # 5: ESE (3, -1)
    # 6: SE (2, -2)
    # 7: SSE (1, -3)
    # 8: S (0, -3)
    # 9: SSW (-1, -3)
    # 10: SW (-2, -2)
    # 11: WSW (-3, -1)
    # 12: W (-3, 0)
    # 13: WNW (-3, 1)
    # 14: NW (-2, 2)
    # 15: NNW (-1, 3)
    
    # So CW starting from North would be:
    # 0, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1
    
    for i, w in enumerate(waves):
        if len(w) < 6:
            continue
        
        # Sort by Base ID
        base_offsets = [None] * 7
        for p in w:
            bid = get_base_id(p.x, p.y)
            if bid != -1:
                nx, ny = nexus_coords[bid]
                base_offsets[bid] = (p.x - nx, p.y - ny)
                
        print(f"\nWave {i+1:2d} (Frame {w[0].frame:5d}, size {len(w)}):")
        # Print for CCW_North
        map_cn = mappings["CCW_North"]
        digits = []
        for val in base_offsets:
            if val is not None:
                digits.append(f"{map_cn[val]:x}")
            else:
                digits.append("?")
        print(f"  Base-sorted CCW_North: {' '.join(digits)}")
        
        # Chronological
        chrono_digits = []
        for p in w:
            bid = get_base_id(p.x, p.y)
            if bid != -1:
                nx, ny = nexus_coords[bid]
                off = (p.x - nx, p.y - ny)
                chrono_digits.append(f"{map_cn[off]:x}")
        print(f"  Chrono CCW_North:      {' '.join(chrono_digits)}")

if __name__ == '__main__':
    main()
