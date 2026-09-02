import sc2reader
from sc2reader.decoders import BitPackedDecoder

def parse_file(path):
    with open(path, 'rb') as f:
        data = f.read()
    try:
        decoded = BitPackedDecoder(data).read_struct()
        print(f"Decoded {path} successfully:")
        import pprint
        pprint.pprint(decoded)
    except Exception as e:
        print(f"Failed to decode {path}: {e}")

parse_file('extracted_replay/replay.details')
