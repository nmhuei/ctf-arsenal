import sc2reader
from sc2reader.decoders import BitPackedDecoder

def try_decrypt(path, xor_key):
    with open(path, 'rb') as f:
        data = bytearray(f.read())
    
    # XOR decrypt
    decrypted = bytearray(b ^ xor_key for b in data)
    
    try:
        decoded = BitPackedDecoder(bytes(decrypted)).read_struct()
        print(f"SUCCESS raw decode with {path} using key {hex(xor_key)}!")
        import pprint
        pprint.pprint(decoded)
    except Exception as e:
        print(f"Failed raw decode for {path} with key {hex(xor_key)}: {e}")

try_decrypt('extracted_replay/replay.details', 0xdd)
try_decrypt('extracted_replay/replay.details.backup', 0xd3)
