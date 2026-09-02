import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    probes = [ev for ev in events if ev.__class__.__name__ == 'UnitBornEvent' and ev.control_pid == 2 and ev.unit_type_name == 'Probe']
    probes.sort(key=lambda x: x.frame)
    probes = [p for p in probes if p.frame > 0] # skip start probes
    
    # Group by frame difference <= 50
    waves = []
    current_wave = []
    for p in probes:
        if not current_wave:
            current_wave.append(p)
        else:
            if p.frame - current_wave[-1].frame <= 50:
                current_wave.append(p)
            else:
                waves.append(current_wave)
                current_wave = [p]
    if current_wave:
        waves.append(current_wave)
        
    print(f"Total waves: {len(waves)}")
    for i, w in enumerate(waves):
        print(f"Wave {i+1:2d} (Frame {w[0].frame}): size {len(w)}")
        # print coords
        print(f"  Coords: {[(p.x, p.y) for p in w]}")

if __name__ == '__main__':
    main()
