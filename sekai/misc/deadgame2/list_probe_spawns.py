import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def list_probes():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    probes = [ev for ev in events if ev.__class__.__name__ == 'UnitBornEvent' and ev.control_pid == 2 and ev.unit_type_name == 'Probe']
    probes.sort(key=lambda x: x.frame)
    
    print(f"Total Probes: {len(probes)}")
    
    # Let's group them if frames are close (within 200 frames)
    groups = []
    current_group = []
    for p in probes:
        if not current_group:
            current_group.append(p)
        else:
            if p.frame - current_group[-1].frame < 200:
                current_group.append(p)
            else:
                groups.append(current_group)
                current_group = [p]
    if current_group:
        groups.append(current_group)
        
    for i, g in enumerate(groups):
        print(f"\nGroup {i+1} (Frames {g[0].frame} - {g[-1].frame}, size {len(g)}):")
        for p in g:
            print(f"  Frame {p.frame:5d}: ({p.x}, {p.y})")

list_probes()
