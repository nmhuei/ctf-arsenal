from sc2reader.decoders import BitPackedDecoder

class MockReplay:
    base_build = 96999

def parse_initdata(path):
    with open(path, 'rb') as f:
        data = f.read()
    
    from sc2reader.readers import InitDataReader
    reader = InitDataReader()
    replay = MockReplay()
    try:
        res = reader(data, replay)
        print("Player names:")
        for idx, u in enumerate(res.get('user_initial_data', [])):
            if u['name']:
                print(f"  Player {idx+1}: {u['name']}")
        print(f"Map File Name: {res['game_description']['map_file_name']}")
    except Exception as e:
        print(f"Failed to parse: {e}")

parse_initdata('extracted_replay/replay.initData.backup')
