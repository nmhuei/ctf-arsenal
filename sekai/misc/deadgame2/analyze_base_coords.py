import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    probes = [ev for ev in events if ev.__class__.__name__ == 'UnitBornEvent' and ev.control_pid == 2 and ev.unit_type_name == 'Probe']
    probes = [p for p in probes if p.frame > 0]
    
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

    base_coords = {i: {} for i in range(7)}
    for p in probes:
        bid = get_base_id(p.x, p.y)
        if bid != -1:
            coord = (p.x, p.y)
            base_coords[bid][coord] = base_coords[bid].get(coord, 0) + 1
            
    for bid in range(7):
        print(f"\nBase {bid}:")
        for coord, count in sorted(base_coords[bid].items(), key=lambda x: x[1], reverse=True):
            print(f"  {coord}: {count} times")

if __name__ == '__main__':
    main()
