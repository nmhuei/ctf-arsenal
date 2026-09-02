import mpyq
import struct
import zlib
import bz2
from io import BytesIO

MPQ_FILE_EXISTS = 0x80000000
MPQ_FILE_ENCRYPTED = 0x00010000
MPQ_FILE_SINGLE_UNIT = 0x01000000
MPQ_FILE_COMPRESS = 0x00000200

def read_block_directly(archive, block_entry):
    def decompress(data):
        compression_type = ord(data[0:1])
        if compression_type == 0:
            return data
        elif compression_type == 2:
            return zlib.decompress(data[1:], 15)
        elif compression_type == 16:
            return bz2.decompress(data[1:])
        else:
            raise RuntimeError(f"Unsupported compression type: {compression_type}")

    if block_entry.flags & MPQ_FILE_EXISTS:
        if block_entry.size == 0:
            return None

        offset = block_entry.offset + archive.header['offset']
        archive.file.seek(offset)
        file_data = archive.file.read(block_entry.archived_size)

        if block_entry.flags & MPQ_FILE_ENCRYPTED:
            raise NotImplementedError("Encryption is not supported yet.")

        if not block_entry.flags & MPQ_FILE_SINGLE_UNIT:
            sector_size = 512 << archive.header['sector_size_shift']
            sectors = block_entry.size // sector_size + 1
            if block_entry.flags & MPQ_FILE_SECTOR_CRC:
                crc = True
                sectors += 1
            else:
                crc = False
            positions = struct.unpack('<%dI' % (sectors + 1), file_data[:4*(sectors+1)])
            result = BytesIO()
            sector_bytes_left = block_entry.size
            for i in range(len(positions) - (2 if crc else 1)):
                sector = file_data[positions[i]:positions[i+1]]
                if (block_entry.flags & MPQ_FILE_COMPRESS and
                    (sector_bytes_left > len(sector))):
                    sector = decompress(sector)
                sector_bytes_left -= len(sector)
                result.write(sector)
            file_data = result.getvalue()
        else:
            if (block_entry.flags & MPQ_FILE_COMPRESS and
                block_entry.size > block_entry.archived_size):
                file_data = decompress(file_data)

        return file_data
    return None

replay_path = 'misc_deadgame2/DeadGame2.SC2Replay'
archive = mpyq.MPQArchive(replay_path)

for block_idx in range(len(archive.block_table)):
    block = archive.block_table[block_idx]
    print(f"\nBlock {block_idx}: offset={block.offset}, size={block.size}, archived_size={block.archived_size}, flags={hex(block.flags)}")
    try:
        data = read_block_directly(archive, block)
        print(f"  Data length: {len(data) if data else 0}")
        if data:
            print(f"  First 100 bytes (hex): {data[:100].hex(' ')}")
            print(f"  First 100 bytes (ASCII): {data[:100]}")
            with open(f"extracted_replay/block_{block_idx}.bin", "wb") as f:
                f.write(data)
    except Exception as e:
        print(f"  Failed to read: {e}")
