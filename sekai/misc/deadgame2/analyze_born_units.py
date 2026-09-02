import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def analyze_born_units(path):
    with open(path, 'rb') as f:
        data = f.read()
        
    from sc2reader.readers import TrackerEventsReader
    reader = TrackerEventsReader()
    replay = MockReplay()
    events = reader(data, replay)
    
    player_units = {1: [], 2: []}
    
    for ev in events:
        if ev.__class__.__name__ == 'UnitBornEvent':
            pid = ev.control_pid
            if pid in (1, 2):
                player_units[pid].append((ev.frame, ev.unit_type_name, ev.x, ev.y))
                
    for pid in (1, 2):
        print(f"\n--- Player {pid} Units Born (total {len(player_units[pid])}) ---")
        # Print first 50 units
        for frame, utype, x, y in player_units[pid][:50]:
            print(f"  Frame {frame:<6}: {utype:<20} at ({x}, {y})")
        if len(player_units[pid]) > 50:
            print(f"  ... and {len(player_units[pid]) - 50} more")

analyze_born_units('extracted_replay/replay.tracker.events')
