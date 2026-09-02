import sc2reader

class MockReplay:
    build = 91118
    base_build = 91118
    opt = {'debug': False}

def parse_game_events():
    with open('extracted_replay/replay.game.events', 'rb') as f:
        data = f.read()
    
    reader = sc2reader.readers.GameEventsReader_80669()
    events = reader(data, MockReplay())
    
    print(f"Total game events: {len(events)}")
    
    event_classes = {}
    for ev in events:
        cls = ev.__class__.__name__
        event_classes[cls] = event_classes.get(cls, 0) + 1
        
    print("\nEvent classes:")
    for cls, cnt in sorted(event_classes.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cls:<30}: {cnt}")
        
    # Check for target-related events
    target_events = []
    for ev in events:
        # check target coordinates
        if hasattr(ev, 'location') and ev.location:
            target_events.append(ev)
        elif hasattr(ev, 'target') and ev.target:
            target_events.append(ev)
            
    print(f"\nTotal events with target/location: {len(target_events)}")
    for ev in target_events[:100]:
        loc = getattr(ev, 'location', None)
        if loc is None:
            loc = getattr(ev, 'target', None)
        ability = getattr(ev, 'ability_name', '')
        print(f"  Frame {ev.frame:5d}: {ev.__class__.__name__} {ability} at {loc}")

parse_game_events()
