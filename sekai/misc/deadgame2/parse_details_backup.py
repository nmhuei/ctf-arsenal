import sc2reader
from sc2reader.decoders import BitPackedDecoder

class MockReplay:
    build = 96999
    base_build = 96999
    versions = [1, 5, 0, 15, 96999]

def parse_details(path):
    with open(path, 'rb') as f:
        data = f.read()
    try:
        from sc2reader.readers import DetailsReader
        reader = DetailsReader()
        replay = MockReplay()
        res = reader(data, replay)
        import pprint
        pprint.pprint(res)
    except Exception as e:
        print(f"Failed to decode {path}: {e}")

parse_details('extracted_replay/replay.details.backup')
