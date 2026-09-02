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

    # Track current offset for each base
    current_offsets = {i: None for i in range(7)}
    changes = []
    
    for p in probes:
        bid = get_base_id(p.x, p.y)
        if bid != -1:
            nx, ny = nexus_coords[bid]
            offset = (p.x - nx, p.y - ny)
            if current_offsets[bid] != offset:
                current_offsets[bid] = offset
                changes.append((p.frame, bid, offset))
                
    print(f"Total rally changes: {len(changes)}")
    for frame, bid, offset in changes:
        print(f"  Frame {frame:5d}: Base {bid} changed to {offset}")

if __name__ == '__main__':
    main()
