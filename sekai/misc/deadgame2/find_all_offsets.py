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
            
    unique_offsets = set(offsets)
    print(f"Total unique offsets: {len(unique_offsets)}")
    
    # Calculate angle for each unique offset (using math.atan2(dy, dx))
    sorted_offsets = []
    for dx, dy in unique_offsets:
        angle = math.atan2(dy, dx)
        # convert to degrees [0, 360)
        deg = math.degrees(angle)
        if deg < 0:
            deg += 360
        sorted_offsets.append((deg, (dx, dy)))
        
    sorted_offsets.sort(key=lambda x: x[0])
    
    # Print sorted offsets with their counts
    for deg, (dx, dy) in sorted_offsets:
        count = offsets.count((dx, dy))
        print(f"  Angle {deg:5.1f}° | Offset ({dx:+d}, {dy:+d}) | Count: {count:3d}")

if __name__ == '__main__':
    main()
