import sc2reader

class MockReplay:
    build = 96999
    base_build = 96999

def main():
    # Load game events
    # We monkeypatch as usual
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
    
    print("Move commands by Player 2 (Protoss):")
    for ev in replay.game_events:
        if ev.__class__.__name__ in ('TargetPointCommandEvent', 'UpdateTargetPointCommandEvent'):
            if ev.player and ev.player.pid == 2:
                # We ignore Revelation (ability name 'Revelation' or similar) and Recall
                ability_name = getattr(ev, 'ability_name', '')
                if 'Revelation' not in ability_name and 'Recall' not in ability_name:
                    loc = getattr(ev, 'location', getattr(ev, 'target', None))
                    if loc:
                        print(f"  Frame {ev.frame:5d}: Move target at ({loc[0]:.2f}, {loc[1]:.2f}) - Ability: {ability_name}")

if __name__ == '__main__':
    main()
