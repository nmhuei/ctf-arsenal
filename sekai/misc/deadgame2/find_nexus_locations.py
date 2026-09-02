import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    nexuses = []
    for ev in events:
        if ev.__class__.__name__ in ('UnitBornEvent', 'UnitInitEvent'):
            if ev.unit_type_name == 'Nexus':
                nexuses.append((ev.x, ev.y, ev.frame))
                
    print("Nexus locations in replay:")
    for n in nexuses:
        print(f"  Frame {n[2]:5d}: Nexus at ({n[0]}, {n[1]})")

if __name__ == '__main__':
    main()
