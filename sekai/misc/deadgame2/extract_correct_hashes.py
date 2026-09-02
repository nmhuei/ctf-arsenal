with open('extracted_replay/block_16.bin', 'rb') as f:
    data = f.read()

# 17 blocks in the block table
num_blocks = 17

crcs = []
for i in range(num_blocks):
    offset = 8 + i * 4
    crc = int.from_bytes(data[offset:offset+4], 'little')
    crcs.append(crc)

md5s = []
for i in range(num_blocks):
    offset = 76 + i * 16
    md5 = data[offset:offset+16].hex()
    md5s.append(md5)

filenames = [
    'replay.details',              # Block 0
    'replay.details.backup',       # Block 1
    'replay.gamemetadata.json',    # Block 2
    'replay.initData',             # Block 3
    'replay.initData.backup',      # Block 4
    'replay.server.battlelobby',   # Block 5
    'replay.game.events',          # Block 6
    'replay.message.events',       # Block 7
    'replay.load.info',            # Block 8
    'replay.sync.events',          # Block 9
    'replay.sync.history',         # Block 10
    'replay.tracker.events',       # Block 11
    'replay.smartcam.events',      # Block 12
    'replay.attributes.events',    # Block 13
    'replay.resumable.events',     # Block 14
    '(listfile)',                  # Block 15
    '(attributes)'                 # Block 16
]

print("Real expected hashes (aligned):")
for i in range(num_blocks):
    print(f"Block {i:2d} ({filenames[i]}):")
    print(f"  Expected CRC: {crcs[i]:#010x}")
    print(f"  Expected MD5: {md5s[i]}")
