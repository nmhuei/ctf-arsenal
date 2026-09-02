with open('extracted_replay/block_16.bin', 'rb') as f:
    data = f.read()

# Header: version (4 bytes), flags (4 bytes)
print(f"Header: {data[:8].hex(' ')}")

# The remaining bytes are entries for 17 blocks.
# Let's print each entry as raw hex bytes.
# Entry format:
# - CRC (4 bytes)
# - MD5 (16 bytes)
# Total 20 bytes.
offset = 8
for i in range(17):
    entry_data = data[offset:offset+20]
    print(f"Block {i:2d} entry: {entry_data.hex(' ')}")
    offset += 20
