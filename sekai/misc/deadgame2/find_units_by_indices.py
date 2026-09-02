import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    target_indices = {453, 468, 640, 667, 752, 850, 394, 471, 511, 678, 656, 704, 455, 653, 655}
    
    print("Units matching tracked indices:")
    for ev in events:
        if ev.__class__.__name__ in ('UnitBornEvent', 'UnitInitEvent'):
            if ev.unit_id_index in target_indices:
                print(f"  Frame {ev.frame:5d}: {ev.unit_type_name} ID={ev.unit_id} (index={ev.unit_id_index}, recycle={ev.unit_id_recycle}) born at ({ev.x}, {ev.y}) owner={ev.control_pid}")

if __name__ == '__main__':
    main()
