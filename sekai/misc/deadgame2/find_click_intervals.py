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
    
    # We want to group click events (TargetPointCommandEvent, UpdateTargetPointCommandEvent)
    # when the time gap between consecutive events is > 500 frames.
    clicks = []
    for ev in replay.game_events:
        cls = ev.__class__.__name__
        if cls in ('TargetPointCommandEvent', 'UpdateTargetPointCommandEvent'):
            clicks.append(ev)
            
    print(f"Total click events: {len(clicks)}")
    
    if not clicks:
        return
        
    intervals = []
    current_interval = [clicks[0]]
    for c in clicks[1:]:
        if c.frame - current_interval[-1].frame < 500:
            current_interval.append(c)
        else:
            intervals.append(current_interval)
            current_interval = [c]
    if current_interval:
        intervals.append(current_interval)
        
    print(f"Found {len(intervals)} click intervals:")
    for i, g in enumerate(intervals):
        frames = [c.frame for c in g]
        xs = [getattr(c, 'location', getattr(c, 'target', (0,0)))[0] for c in g]
        ys = [getattr(c, 'location', getattr(c, 'target', (0,0)))[1] for c in g]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        print(f"  Interval {i+1}: Frames {frames[0]:5d} - {frames[-1]:5d} (size {len(g):4d}) | X: [{min_x:.1f}, {max_x:.1f}] Y: [{min_y:.1f}, {max_y:.1f}]")

if __name__ == '__main__':
    main()
