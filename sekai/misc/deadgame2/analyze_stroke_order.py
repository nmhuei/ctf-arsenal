import sc2reader
import numpy as np

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    # Load game events
    from sc2reader.decoders import BitPackedDecoder
    from sc2reader.readers import DetailsReader
    import hashlib

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

    replay = sc2reader.load_replay('misc_deadgame2/DeadGame2.SC2Replay', load_level=4)
    
    clicks = []
    for ev in replay.game_events:
        if ev.__class__.__name__ in ('TargetPointCommandEvent', 'UpdateTargetPointCommandEvent'):
            if ev.player and ev.player.pid == 2:
                ability_name = getattr(ev, 'ability_name', '')
                if 'Revelation' not in ability_name and 'Recall' not in ability_name:
                    loc = getattr(ev, 'location', getattr(ev, 'target', None))
                    if loc:
                        clicks.append((loc[0], loc[1], ev.frame))
                        
    drawing_clicks = [c for c in clicks if 110 <= c[0] <= 135 and 95 <= c[1] <= 112]
    
    # Group clicks into strokes
    strokes = []
    current_stroke = [drawing_clicks[0]]
    for i in range(1, len(drawing_clicks)):
        prev = drawing_clicks[i-1]
        curr = drawing_clicks[i]
        dist = np.sqrt((curr[0]-prev[0])**2 + (curr[1]-prev[1])**2)
        frame_gap = curr[2] - prev[2]
        if dist > 4.5 or frame_gap > 100:
            strokes.append(current_stroke)
            current_stroke = [curr]
        else:
            current_stroke.append(curr)
    if current_stroke:
        strokes.append(current_stroke)
        
    print("Strokes in chronological order:")
    for idx, stroke in enumerate(strokes):
        xs = [p[0] for p in stroke]
        ys = [p[1] for p in stroke]
        start_frame = stroke[0][2]
        end_frame = stroke[-1][2]
        print(f"  Stroke {idx+1:2d}: Frames {start_frame:5d} to {end_frame:5d} | X: {min(xs):5.1f} to {max(xs):5.1f} | Y: {min(ys):5.1f} to {max(ys):5.1f} | Len: {len(stroke)}")

if __name__ == '__main__':
    main()
