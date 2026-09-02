import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    target_indices = {804, 660, 778}
    
    print("Tracing Observer movement via UnitPositionsEvent:")
    for ev in events:
        if ev.__class__.__name__ == 'UnitPositionsEvent':
            if hasattr(ev, 'positions') and ev.positions:
                for idx, pos in ev.positions:
                    if idx in target_indices:
                        print(f"  Frame {ev.frame:5d}: Observer {idx} at {pos}")

if __name__ == '__main__':
    main()
