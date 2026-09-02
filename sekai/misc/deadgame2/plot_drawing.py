import sc2reader
import matplotlib.pyplot as plt

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    # Load game events
    # We monkeypatch the DetailsReader and BitPackedDecoder as usual
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
    
    # Extract clicks of Player 2 between 71648 and 72475
    points = []
    for ev in replay.game_events:
        if 71000 <= ev.frame <= 73000:
            if ev.__class__.__name__ in ('TargetPointCommandEvent', 'UpdateTargetPointCommandEvent'):
                if ev.player and ev.player.pid == 2:
                    loc = getattr(ev, 'location', getattr(ev, 'target', None))
                    if loc:
                        points.append((loc[0], loc[1], ev.frame))
                        
    print(f"Extracted {len(points)} points.")
    
    if not points:
        return
        
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    
    plt.figure(figsize=(10, 6))
    plt.scatter(xs, ys, c=[p[2] for p in points], cmap='viridis', s=15)
    plt.colorbar(label='Frame')
    plt.title('Player 2 clicks (drawing) between 71648 and 72475')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    
    # Save the figure to artifact directory
    import os
    os.makedirs('/home/light/.gemini/antigravity/brain/6d5769a3-a175-4214-a3ab-7760ac05ba6b/artifacts', exist_ok=True)
    plt.savefig('/home/light/.gemini/antigravity/brain/6d5769a3-a175-4214-a3ab-7760ac05ba6b/artifacts/drawing.png')
    print("Saved plot to artifacts/drawing.png")

if __name__ == '__main__':
    main()
