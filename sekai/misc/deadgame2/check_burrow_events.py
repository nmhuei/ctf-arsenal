import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    burrow_frames = [39808, 43238, 47063, 58662, 59843]
    
    for bf in burrow_frames:
        print(f"\nEvents around Burrow frame {bf}:")
        for ev in events:
            if bf - 50 <= ev.frame <= bf + 100:
                loc_str = ""
                if hasattr(ev, 'x') and hasattr(ev, 'y'):
                    loc_str = f" at ({ev.x}, {ev.y})"
                # Unit type / ID if available
                unit_str = ""
                if hasattr(ev, 'unit_type_name'):
                    unit_str = f" unit_type={ev.unit_type_name}"
                elif hasattr(ev, 'unit_id'):
                    unit_str = f" unit_id={ev.unit_id}"
                
                print(f"  Frame {ev.frame:5d}: {ev.__class__.__name__}{unit_str}{loc_str}")

if __name__ == '__main__':
    main()
