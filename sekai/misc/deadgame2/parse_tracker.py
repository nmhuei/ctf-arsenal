import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def parse_tracker(path):
    with open(path, 'rb') as f:
        data = f.read()
        
    from sc2reader.readers import TrackerEventsReader
    reader = TrackerEventsReader()
    replay = MockReplay()
    events = reader(data, replay)
    
    for ev in events:
        if ev.__class__.__name__ == 'UnitBornEvent':
            print("UnitBornEvent attributes:")
            import pprint
            pprint.pprint(vars(ev))
            break
            
    for ev in events:
        if ev.__class__.__name__ == 'UnitPositionsEvent':
            print("\nUnitPositionsEvent attributes:")
            import pprint
            pprint.pprint(vars(ev))
            break

parse_tracker('extracted_replay/replay.tracker.events')
