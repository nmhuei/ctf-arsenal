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
    
    # Exclude initial 12 probes (frame 0)
    probes = [p for p in probes if p.frame > 0]
    
    print(f"Total Probes (after frame 0): {len(probes)}")
    
    # Split into groups of 7
    num_waves = len(probes) // 7
    remainder = len(probes) % 7
    print(f"Number of groups of 7: {num_waves}, Remainder: {remainder}")
    
    for i in range(num_waves):
        group = probes[i*7 : (i+1)*7]
        frames = [p.frame for p in group]
        coords = [(p.x, p.y) for p in group]
        print(f"Group {i+1:2d}: Frames {min(frames):5d}-{max(frames):5d} | Coords: {coords}")
        
    if remainder > 0:
        group = probes[num_waves*7:]
        frames = [p.frame for p in group]
        coords = [(p.x, p.y) for p in group]
        print(f"Remainder Group: Frames {min(frames):5d}-{max(frames):5d} | Coords: {coords}")

if __name__ == '__main__':
    main()
