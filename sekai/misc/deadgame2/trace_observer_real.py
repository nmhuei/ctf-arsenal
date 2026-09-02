import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    # Observer births:
    # Observer ID=210763801 (index=804) born at frame 64653
    # Observer ID=173015044 (index=660) born at frame 64657
    # Observer ID=203948034 (index=778) born at frame 64660
    
    obs_births = {
        804: 64653,
        660: 64657,
        778: 64660
    }
    
    print("Observer positions after birth:")
    for ev in events:
        if ev.__class__.__name__ == 'UnitPositionsEvent':
            if hasattr(ev, 'positions') and ev.positions:
                for idx, pos in ev.positions:
                    if idx in obs_births and ev.frame >= obs_births[idx]:
                        print(f"  Frame {ev.frame:5d}: Observer {idx} at {pos}")

if __name__ == '__main__':
    main()
