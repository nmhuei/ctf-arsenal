import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    count = 0
    for ev in events:
        if ev.__class__.__name__ == 'UnitPositionsEvent':
            if ev.units:
                count += 1
                print(f"Frame {ev.frame}: {len(ev.units)} units tracked")
                if count >= 10:
                    break

if __name__ == '__main__':
    main()
