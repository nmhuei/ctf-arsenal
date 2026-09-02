import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    unit_types = {}
    for ev in events:
        if ev.__class__.__name__ in ('UnitBornEvent', 'UnitInitEvent'):
            ut = ev.unit_type_name
            unit_types[ut] = unit_types.get(ut, 0) + 1
            
    print("Unit types born/initialized in replay:")
    for ut, count in sorted(unit_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ut}: {count}")

if __name__ == '__main__':
    main()
