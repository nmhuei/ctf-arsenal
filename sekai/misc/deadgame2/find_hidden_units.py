import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    with open('extracted_replay/replay.tracker.events', 'rb') as f:
        data = f.read()
    events = sc2reader.readers.TrackerEventsReader()(data, MockReplay())
    
    units = []
    ignored_types = {
        'MineralField', 'MineralField750', 'VespeneGeyser', 'RichMineralField',
        'RichMineralField750', 'RichVespeneGeyser', 'UnbuildableRocksDestructible',
        'BeaconArmy', 'BeaconDefend', 'BeaconAttack', 'BeaconHarass',
        'BeaconIdle', 'BeaconAuto', 'BeaconDetect', 'BeaconScout',
        'BeaconClaim', 'BeaconExpand', 'BeaconRally', 'BeaconCustom1',
        'BeaconCustom2', 'BeaconCustom3', 'BeaconCustom4', 'Larva', 'Zergling',
        'Drone', 'Probe', 'Pylon', 'Hatchery', 'Nexus', 'Queen', 'Extractor',
        'Assimilator', 'RoboticsFacility', 'Stargate', 'Forge', 'Observer',
        'Carrier', 'Interceptor', 'Mothership', 'DarkShrine', 'TwilightCouncil',
        'Gateway', 'CyberneticsCore', 'BanelingNest', 'EvolutionChamber',
        'SpawningPool', 'Stalker', 'Baneling', 'Roach', 'Overlord',
        'TemplarArchive', 'FleetBeacon', 'Oracle'
    }
    
    for ev in events:
        if ev.__class__.__name__ in ('UnitBornEvent', 'UnitInitEvent'):
            if ev.unit_type_name not in ignored_types:
                units.append((ev.unit_type_name, ev.x, ev.y, ev.frame, ev.control_pid))
                
    print(f"Found {len(units)} custom/non-standard units:")
    for u in sorted(units, key=lambda x: x[3]):
        print(f"  Frame {u[3]:5d}: {u[0]} at ({u[1]}, {u[2]}) owned by Player {u[4]}")

if __name__ == '__main__':
    main()
