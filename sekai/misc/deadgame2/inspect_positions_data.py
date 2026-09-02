import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    for ev in events:
        if ev.__class__.__name__ == 'UnitPositionsEvent':
            if hasattr(ev, 'positions') and ev.positions:
                print(f"Frame {ev.frame}: first_unit_index={ev.first_unit_index}, positions={ev.positions[:10]}")
                break

if __name__ == '__main__':
    main()
