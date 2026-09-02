import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def list_larva():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    larvae = [ev for ev in events if ev.__class__.__name__ == 'UnitBornEvent' and ev.control_pid == 1 and ev.unit_type_name == 'Larva']
    larvae.sort(key=lambda x: x.frame)
    
    print(f"Total Larvae: {len(larvae)}")
    
    groups = []
    current_group = []
    for l in larvae:
        if not current_group:
            current_group.append(l)
        else:
            if l.frame - current_group[-1].frame < 200:
                current_group.append(l)
            else:
                groups.append(current_group)
                current_group = [l]
    if current_group:
        groups.append(current_group)
        
    for i, g in enumerate(groups):
        print(f"\nGroup {i+1} (Frames {g[0].frame} - {g[-1].frame}, size {len(g)}):")
        for l in g:
            print(f"  Frame {l.frame:5d}: ({l.x}, {l.y})")

list_larva()
