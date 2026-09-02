import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    print("UnitPositionsEvents after frame 64650:")
    for ev in events:
        if ev.__class__.__name__ == 'UnitPositionsEvent' and ev.frame >= 64650:
            if hasattr(ev, 'positions') and ev.positions:
                print(f"  Frame {ev.frame:5d}: {ev.positions}")

if __name__ == '__main__':
    main()
