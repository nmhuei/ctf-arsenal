import sc2reader
from sc2reader.decoders import BitPackedDecoder
from sc2reader.readers import DetailsReader
import hashlib

# 1. Monkeypatch BitPackedDecoder.read_struct to bypass corrupted header
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

# 2. Monkeypatch DetailsReader to bypass corrupted details
class MockCacheHandle:
    server = 'us'
    hash = hashlib.sha256(b"Standard Data: Void.SC2Mod").hexdigest()

def mock_details_reader(self, data, replay):
    player1_mock = {
        "result": 1,
        "race": "Zerg",
        "color": {"r": 255, "g": 0, "b": 0, "a": 255},
        "bnet": {"region": 1, "subregion": 1, "uid": 1}
    }
    player2_mock = {
        "result": 2,
        "race": "Protoss",
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

# 3. Try to load the replay using sc2reader
try:
    replay = sc2reader.load_replay('misc_deadgame2/DeadGame2.SC2Replay', load_level=4)
    print("Replay loaded successfully!")
    print(f"Build: {replay.build}")
    print(f"Map: {replay.map_name}")
    print(f"Total game events: {len(replay.game_events)}")
    
    # Check resolved ability names!
    cmd_events = [ev for ev in replay.game_events if 'Cmd' in ev.__class__.__name__ or 'Command' in ev.__class__.__name__]
    print(f"Total command events: {len(cmd_events)}")
    
    # Print distinct ability names
    abilities = set(getattr(ev, 'ability_name', 'Unknown') for ev in cmd_events)
    print(f"Unique ability names in game events: {sorted(list(abilities))}")
    
except Exception as e:
    import traceback
    traceback.print_exc()
