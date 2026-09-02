import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    # We want to trace all Observers. First let's find their unit IDs.
    obs_ids = {}
    for ev in events:
        if ev.__class__.__name__ in ('UnitBornEvent', 'UnitInitEvent'):
            if ev.unit_type_name == 'Observer':
                obs_ids[ev.unit_id] = {
                    'born_frame': ev.frame,
                    'born_coords': (ev.x, ev.y),
                    'positions': []
                }
                
    # Now look at UnitPositionsEvent to trace them
    for ev in events:
        if ev.__class__.__name__ == 'UnitPositionsEvent':
            # In sc2reader, UnitPositionsEvent has a 'units' dictionary: unit_index -> (x, y)
            for unit_index, (x, y) in ev.units.items():
                # Note: unit_id in UnitBornEvent is (unit_index << 6) | unit_tag or similar?
                # Actually, sc2reader UnitPositionsEvent units dictionary keys are unit_index.
                # Let's match by unit_index.
                # In sc2reader, unit_index in UnitPositionsEvent matches (ev.unit_id >> 6)?
                # Let's check: ev.unit_id_index is the index, ev.unit_id_recycle is the recycle.
                # Let's verify what the keys in UnitPositionsEvent are.
                pass
                
    # Alternatively, let's just search for all events involving Observers (like UnitBornEvent, UnitDiedEvent, and commands).
    # Since there are only 3 Observers born!
    # Wait, our find_all_births.py output said:
    # Observer: 3!
    # So there are only 3 Observers in the entire game!
    # Let's print everything about these 3 Observers.
    print("Observer Births:")
    for ev in events:
        if ev.__class__.__name__ in ('UnitBornEvent', 'UnitInitEvent') and ev.unit_type_name == 'Observer':
            print(f"  Frame {ev.frame:5d}: Observer ID={ev.unit_id} (index={ev.unit_id_index}, recycle={ev.unit_id_recycle}) born at ({ev.x}, {ev.y})")
            
    # Let's find any commands targeted at these Observers, or UnitPositionsEvent matching them.
    # UnitPositionsEvent has `units` attribute which is a dict of unit_id_index -> (x, y)
    print("\nTracing Observer positions over time:")
    for ev in events:
        if ev.__class__.__name__ == 'UnitPositionsEvent':
            for idx, (x, y) in ev.units.items():
                # Check if this idx matches any of our Observers
                for ob_id, info in obs_ids.items():
                    if (ob_id >> 6) == idx:
                        print(f"  Frame {ev.frame:5d}: Observer {ob_id} at ({x}, {y})")
                        
    # Let's print all UnitDiedEvents for Observers
    for ev in events:
        if ev.__class__.__name__ == 'UnitDiedEvent':
            for ob_id in obs_ids:
                if ev.unit_id == ob_id:
                    print(f"  Frame {ev.frame:5d}: Observer {ob_id} DIED at ({ev.x}, {ev.y})")

if __name__ == '__main__':
    main()
