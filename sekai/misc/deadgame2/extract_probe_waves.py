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
    
    # 1. Group probes into waves (gap < 200 frames)
    waves = []
    current_wave = []
    for p in probes:
        if not current_wave:
            current_wave.append(p)
        else:
            if p.frame - current_wave[-1].frame < 200:
                current_wave.append(p)
            else:
                waves.append(current_wave)
                current_wave = [p]
    if current_wave:
        waves.append(current_wave)
        
    print(f"Total waves found: {len(waves)}")
    
    # Filter waves that have size ~7 (let's print waves with size between 4 and 7)
    # Actually, let's define the 7 bases based on the known locations:
    # We can classify coordinates (x, y) into 7 bases:
    # Base 0: Main base (x > 195, y < 65)
    # Base 1: Natural (170 <= x <= 190, y < 65)
    # Base 2: Third (x > 195, 75 <= y <= 85)
    # Base 3: Middle Right (100 <= x <= 120, 65 <= y <= 75)
    # Base 4: Middle Left (90 <= x < 100, 65 <= y <= 75)
    # Base 5: Zerg Third (60 <= x <= 70, 75 <= y <= 85)
    # Base 6: Zerg Natural (60 <= x <= 70, y >= 90)
    
    def get_base_id(x, y):
        if x > 195 and y < 65:
            return 0
        elif 170 <= x <= 190 and y < 65:
            return 1
        elif x > 195 and 75 <= y <= 85:
            return 2
        elif 100 <= x <= 120 and 65 <= y <= 75:
            return 3
        elif 90 <= x < 100 and 65 <= y <= 75:
            return 4
        elif 60 <= x <= 70 and 75 <= y <= 85:
            return 5
        elif 60 <= x <= 70 and y >= 90:
            return 6
        else:
            return -1

    # Let's print details of each wave of size >= 6
    valid_wave_index = 0
    for idx, w in enumerate(waves):
        # We skip the initial 12 probes spawned at frame 0 (which is the starting worker count)
        if w[0].frame == 0:
            continue
        
        # We also print the size of the wave
        size = len(w)
        # Classify each probe in the wave
        base_probes = {i: None for i in range(7)}
        unclassified = []
        for p in w:
            bid = get_base_id(p.x, p.y)
            if bid != -1:
                base_probes[bid] = (p.x, p.y)
            else:
                unclassified.append((p.x, p.y, p.frame))
                
        valid_wave_index += 1
        print(f"\nWave {valid_wave_index} (Original index {idx+1}, Frame {w[0].frame}, size {size}):")
        for bid in range(7):
            print(f"  Base {bid}: {base_probes[bid]}")
        if unclassified:
            print(f"  Unclassified: {unclassified}")

if __name__ == '__main__':
    main()
