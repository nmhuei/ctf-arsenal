import hashlib
import zlib

# Load the actual blocks
blocks_data = {}
for idx in range(17):
    try:
        with open(f"extracted_replay/block_{idx}.bin", "rb") as f:
            blocks_data[idx] = f.read()
    except:
        blocks_data[idx] = b''

# Read attributes file
with open('extracted_replay/block_16.bin', 'rb') as f:
    attr_data = f.read()

# Let's search for actual CRCs and MD5s in the attributes file
print("Actual block hashes:")
for idx in range(17):
    data = blocks_data[idx]
    crc = zlib.crc32(data) & 0xffffffff
    md5 = hashlib.md5(data).digest()
    
    print(f"Block {idx:2d}: size={len(data):<6} CRC={crc:#010x} MD5={md5.hex()}")
    
    # Let's search for CRC (4 bytes, little-endian) in attr_data
    crc_bytes = crc.to_bytes(4, 'little')
    crc_idx = attr_data.find(crc_bytes)
    md5_idx = attr_data.find(md5[:4]) # search for first 4 bytes of MD5
    
    print(f"  CRC {crc_bytes.hex()} found at index: {crc_idx}")
    print(f"  MD5 {md5[:4].hex()}... found at index: {md5_idx}")
