import sc2reader
from sc2reader.decoders import BitPackedDecoder

class MockReplay:
    base_build = 96999

def parse_messages(path):
    with open(path, 'rb') as f:
        data = f.read()
    
    from sc2reader.readers import MessageEventsReader
    reader = MessageEventsReader()
    replay = MockReplay()
    try:
        res = reader(data, replay)
        print("Messages:")
        for m in res.get('messages', []):
            print(f"  Frame {m.frame} - Player {m.pid}: {m.text}")
        print("Pings:")
        for p in res.get('pings', []):
            print(f"  Frame {p.frame} - Player {p.pid}: ({p.x}, {p.y})")
    except Exception as e:
        print(f"Failed to parse messages: {e}")

parse_messages('extracted_replay/replay.message.events')
