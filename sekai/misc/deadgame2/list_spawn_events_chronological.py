import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def list_chronological():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    # Sort events by frame
    born_events = [ev for ev in events if ev.__class__.__name__ == 'UnitBornEvent']
    born_events.sort(key=lambda x: x.frame)
    
    print(f"Total UnitBornEvents: {len(born_events)}")
    
    print("\nFirst 100 Spawn Events:")
    for i, ev in enumerate(born_events[:100]):
        print(f"Frame {ev.frame:5d}: Player {ev.control_pid} spawned {ev.unit_type_name} at ({ev.x}, {ev.y})")
        
    print("\nLast 100 Spawn Events:")
    for i, ev in enumerate(born_events[-100:]):
        print(f"Frame {ev.frame:5d}: Player {ev.control_pid} spawned {ev.unit_type_name} at ({ev.x}, {ev.y})")

list_chronological()
