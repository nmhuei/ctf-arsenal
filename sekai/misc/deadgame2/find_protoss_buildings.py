import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    buildings = []
    protoss_building_types = {
        'Nexus', 'Pylon', 'Assimilator', 'Gateway', 'Forge', 'CyberneticsCore',
        'PhotonCannon', 'ShieldBattery', 'RoboticsFacility', 'Stargate',
        'TwilightCouncil', 'RoboticsBay', 'FleetBeacon', 'TemplarArchive',
        'DarkShrine'
    }
    
    for ev in events:
        if ev.__class__.__name__ in ('UnitBornEvent', 'UnitInitEvent'):
            if ev.unit_type_name in protoss_building_types and ev.control_pid == 2:
                buildings.append((ev.unit_type_name, ev.x, ev.y, ev.frame))
                
    print("Protoss buildings:")
    for b in sorted(buildings, key=lambda x: x[3]):
        print(f"  Frame {b[3]:5d}: {b[0]} at ({b[1]}, {b[2]})")

if __name__ == '__main__':
    main()
