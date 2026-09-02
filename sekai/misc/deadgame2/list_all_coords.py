import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def list_coords():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    p1_coords = sorted(list(set((ev.x, ev.y) for ev in events if ev.__class__.__name__ == 'UnitBornEvent' and ev.control_pid == 1)))
    p2_coords = sorted(list(set((ev.x, ev.y) for ev in events if ev.__class__.__name__ == 'UnitBornEvent' and ev.control_pid == 2)))
    
    print(f"Player 1 unique spawn coords ({len(p1_coords)}):")
    print(p1_coords)
    
    print(f"\nPlayer 2 unique spawn coords ({len(p2_coords)}):")
    print(p2_coords)

list_coords()
