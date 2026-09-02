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
    
    # Nexus locations:
    nexus_coords = {
        0: (201, 56),
        1: (177, 56),
        2: (201, 78),
        3: (110, 71),
        4: (91, 71),
        5: (60, 78),
        6: (59, 94)
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
        
    for i, w in enumerate(waves):
        # Let's print the offsets for all waves
        offsets = [None] * 7
        for p in w:
            bid = get_base_id(p.x, p.y)
            if bid != -1:
                nx, ny = nexus_coords[bid]
                offsets[bid] = (p.x - nx, p.y - ny)
        print(f"Wave {i+1:2d} (Frame {w[0].frame:5d}): {offsets}")

if __name__ == '__main__':
    main()
