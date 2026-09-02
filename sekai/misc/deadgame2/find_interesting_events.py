import sc2reader
from sc2reader.decoders import BitPackedDecoder
from sc2reader.readers import DetailsReader
import hashlib

# Patching sc2reader
orig_read_struct = BitPackedDecoder.read_struct
def mock_read_struct(self):
    try:
        return orig_read_struct(self)
    except TypeError as e:
        if "Unknown Data Structure: '117'" in str(e):
            return {
                1: {0: 1, 1: 5, 2: 0, 3: 12, 4: 91118, 5: 91118},
                3: 73931
            }
        raise
BitPackedDecoder.read_struct = mock_read_struct

class MockCacheHandle:
    server = 'us'
    hash = hashlib.sha256(b"Standard Data: Void.SC2Mod").hexdigest()

def mock_details_reader(self, data, replay):
    player1_mock = {
        "result": 1, "race": "Zerg",
        "color": {"r": 255, "g": 0, "b": 0, "a": 255},
        "bnet": {"region": 1, "subregion": 1, "uid": 1}
    }
    player2_mock = {
        "result": 2, "race": "Protoss",
        "color": {"r": 0, "g": 0, "b": 255, "a": 255},
        "bnet": {"region": 1, "subregion": 1, "uid": 2}
    }
    return {
        "map_name": "Tunguska",
        "cache_handles": [MockCacheHandle()],
        "file_time": 132470000000000000,
        "utc_adjustment": 0,
        "players": [player1_mock, player2_mock]
    }
DetailsReader.__call__ = mock_details_reader

def main():
    replay = sc2reader.load_replay('misc_deadgame2/DeadGame2.SC2Replay', load_level=4)
    
    print("Listing selected interesting events:")
    ignore_abilities = {
        'RightClick', 'Attack', 'HoldPosition', 'Stop', 'Patrol', 'ReturnCargo',
        'TrainProbe', 'TrainDrone', 'TrainQueen', 'TrainObserver', 'TrainOracle',
        'TrainCarrier', 'TrainMothership', 'MorphDrone', 'MorphOverlord', 'MorphZergling',
        'BuildNexus', 'BuildPylon', 'BuildAssimilator', 'BuildGateway', 'BuildForge',
        'BuildCyberneticsCore', 'BuildTwilightCouncil', 'BuildRoboticsFacility',
        'BuildStargate', 'BuildFleetBeacon', 'BuildDarkShrine', 'BuildTemplarArchive',
        'BuildHatchery', 'BuildExtractor', 'BuildSpawningPool', 'BuildEvolutionChamber',
        'BuildBanelingNest', 'MorphToOverseer', 'ResearchWarpGate', 'ResearchBlink',
        'ResearchCharge', 'ResearchPsiStormTech', 'ResearchGravitySling', 'ResearchAnionPulseCrystals',
        'UpgradeGroundWeapons1', 'UpgradeGroundWeapons2', 'UpgradeGroundWeapons3',
        'UpgradeGroundArmor1', 'UpgradeGroundArmor2', 'UpgradeGroundArmor3',
        'UpgradeShields1', 'UpgradeShields2', 'UpgradesShields3',
        'UpgradeAirWeapons1', 'UpgradeAirWeapons2', 'UpgradeAirWeapons3',
        'UpgradeAirArmor1', 'UpgradeAirArmor2', 'UpgradeAirArmor3',
        'UpgradeToLair', 'ResearchBurrow', 'SpawnLarva', 'WarpInStalker'
    }
    
    for ev in replay.game_events:
        cls = ev.__class__.__name__
        if 'Command' in cls or 'Cmd' in cls:
            if cls == 'CommandManagerStateEvent':
                continue
            ability = getattr(ev, 'ability_name', '')
            if ability in ignore_abilities:
                continue
            loc = getattr(ev, 'location', None)
            if loc is None:
                loc = getattr(ev, 'target', None)
            pid = ev.player.pid if ev.player else 'None'
            print(f"Frame {ev.frame:5d}: Player {pid} cast {ability} (type={cls}) at {loc}")

if __name__ == '__main__':
    main()
