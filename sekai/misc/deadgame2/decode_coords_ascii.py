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
    probes = [p for p in probes if p.frame > 0]
    
    # Try X as ASCII
    print("X coords as ASCII:")
    chars_x = []
    for p in probes:
        c = p.x
        if 32 <= c <= 126:
            chars_x.append(chr(c))
        else:
            chars_x.append('.')
    print("".join(chars_x))
    
    # Try Y as ASCII
    print("\nY coords as ASCII:")
    chars_y = []
    for p in probes:
        c = p.y
        if 32 <= c <= 126:
            chars_y.append(chr(c))
        else:
            chars_y.append('.')
    print("".join(chars_y))

    # Try X ^ Y as ASCII
    print("\nX ^ Y as ASCII:")
    chars_xor = []
    for p in probes:
        c = p.x ^ p.y
        if 32 <= c <= 126:
            chars_xor.append(chr(c))
        else:
            chars_xor.append('.')
    print("".join(chars_xor))

    # Let's check if the coordinates form a sequence of bytes.
    # What if we print the actual numbers (X, Y) for the first 100 Probes?
    print("\nFirst 50 Probe (X, Y):")
    for i, p in enumerate(probes[:50]):
        print(f"  Probe {i+1:2d}: ({p.x}, {p.y})")

if __name__ == '__main__':
    main()
