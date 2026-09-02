import struct

def parse_attributes(path):
    with open(path, 'rb') as f:
        data = f.read()
        
    print(f"Attributes file size: {len(data)}")
    if len(data) < 8:
        print("Too small")
        return
        
    version, flags = struct.unpack('<II', data[:8])
    print(f"Version: {version}, Flags: {flags:#x}")
    
    # Let's see how many entries there should be
    # Standard MPQ attributes has entries for each block in block table!
    # Wait, the number of entries is the number of blocks in the block table (which is 17).
    # If 17 entries:
    # CRC32 is 4 bytes.
    # MD5 is 16 bytes.
    # Total per entry = 20 bytes (if flags == 5).
    # 17 * 20 = 340 bytes.
    # Plus 8 bytes header = 348 bytes!
    # YES! It matches perfectly! 348 bytes!
    
    offset = 8
    print("\nParsed Attributes per Block:")
    for i in range(17):
        crc = None
        md5 = None
        if flags & 1:
            crc = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
        if flags & 2:
            # FileTime (8 bytes)
            filetime = struct.unpack('<Q', data[offset:offset+8])[0]
            offset += 8
        if flags & 4:
            md5 = data[offset:offset+16].hex()
            offset += 16
            
        print(f"Block {i:2d}: CRC={crc:#010x}, MD5={md5}")

parse_attributes('extracted_replay/block_16.bin')
