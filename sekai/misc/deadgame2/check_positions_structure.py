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
            print(f"Frame {ev.frame}: UnitPositionsEvent")
            print(f"  Attributes: {dir(ev)}")
            if hasattr(ev, 'units'):
                print(f"  units type: {type(ev.units)}")
                print(f"  units items sample: {list(ev.units.items())[:5]}")
            break

if __name__ == '__main__':
    main()
