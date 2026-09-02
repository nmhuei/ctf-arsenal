import sc2reader
import matplotlib.pyplot as plt
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
    
    # We want to trace all clicks of Player 2 in the time window 70000 to 73000
    # that are not Revelation or Recall.
    clicks = []
    for ev in replay.game_events:
        if ev.__class__.__name__ in ('TargetPointCommandEvent', 'UpdateTargetPointCommandEvent'):
            if ev.player and ev.player.pid == 2:
                ability_name = getattr(ev, 'ability_name', '')
                if 'Revelation' not in ability_name and 'Recall' not in ability_name:
                    loc = getattr(ev, 'location', getattr(ev, 'target', None))
                    if loc:
                        clicks.append((loc[0], loc[1], ev.frame))
                        
    print(f"Extracted {len(clicks)} clicks.")
    
    # Filter to only the drawing region:
    # 110 <= x <= 135 and 95 <= y <= 112
    drawing_clicks = [c for c in clicks if 110 <= c[0] <= 135 and 95 <= c[1] <= 112]
    print(f"Filtered to {len(drawing_clicks)} drawing clicks.")
    
    if not drawing_clicks:
        return
        
    # Group clicks into strokes if distance > 4 or frame gap > 50
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
        
    print(f"Detected {len(strokes)} strokes.")
    
    plt.figure(figsize=(10, 6))
    for idx, stroke in enumerate(strokes):
        xs = [p[0] for p in stroke]
        ys = [p[1] for p in stroke]
        plt.plot(xs, ys, '-o', label=f'Stroke {idx+1}')
        # label start/end of stroke
        plt.text(xs[0], ys[0], f"S{idx+1}", color='green', fontsize=10, weight='bold')
        plt.text(xs[-1], ys[-1], f"E{idx+1}", color='red', fontsize=10, weight='bold')
        
    plt.legend()
    plt.grid(True)
    plt.title('Player 2 Drawing - Stroke by Stroke')
    plt.xlabel('X')
    plt.ylabel('Y')
    
    import os
    os.makedirs('/home/light/.gemini/antigravity/brain/6d5769a3-a175-4214-a3ab-7760ac05ba6b/artifacts', exist_ok=True)
    plt.savefig('/home/light/.gemini/antigravity/brain/6d5769a3-a175-4214-a3ab-7760ac05ba6b/artifacts/strokes.png')
    print("Saved plot to artifacts/strokes.png")

if __name__ == '__main__':
    main()
