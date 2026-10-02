"""Validate recovered ZIPCrypto keys against locally recovered archive data."""
from pathlib import Path
import ctypes
import json
import struct
import zlib

HERE = Path(__file__).resolve().parent
INITIAL = (0x670e8462, 0x306591b4, 0x8372919d)
TABLE = []
for value in range(256):
    for _ in range(8):
        value = (value >> 1) ^ (0xedb88320 if value & 1 else 0)
    TABLE.append(value)


def decrypt(data):
    a, b, c = INITIAL
    plain = bytearray()
    for encrypted in data:
        temporary = (c & 0xffff) | 2
        value = encrypted ^ (((temporary * (temporary ^ 1)) >> 8) & 255)
        plain.append(value)
        a = (a >> 8) ^ TABLE[(a ^ value) & 255]
        b = ((b + (a & 255)) * 134775813 + 1) & 0xffffffff
        c = (c >> 8) ^ TABLE[(c ^ (b >> 24)) & 255]
    return bytes(plain)


def main():
    archive = (HERE / 'documents_reassembled.zip').read_bytes()
    records = json.loads((HERE / 'archive_records.json').read_text())
    output = HERE / 'decrypted_documents'
    output.mkdir(exist_ok=True)
    results = []
    for record in records:
        position = int(record['logical'], 16)
        header = struct.unpack_from('<4s5H3I2H', archive, position)
        begin = position + 30 + header[9] + header[10]
        end = begin + header[7]
        result = {'name': record['name'], 'complete': end <= len(archive)}
        if result['complete']:
            decrypted = decrypt(archive[begin:end])
            payload = decrypted[12:]
            if header[3] == 8:
                payload = zlib.decompress(payload, -15)
            elif header[3] != 0:
                raise ValueError(f'Unsupported ZIP compression: {header[3]}')
            result['encryption_header'] = decrypted[:12].hex()
            result['crc_valid'] = zlib.crc32(payload) == header[6]
            result['size_valid'] = len(payload) == header[8]
            if result['crc_valid'] and result['size_valid']:
                # Use a basename rather than trusting paths contained in the evidence.
                (output / Path(record['name']).name).write_bytes(payload)
        results.append(result)

    libc = ctypes.CDLL('libc.so.6')
    libc.srand.argtypes = [ctypes.c_uint]
    libc.rand.restype = ctypes.c_int
    target = bytes.fromhex(results[0]['encryption_header'])[:11]
    matches = []
    for seed in range(1788884900, 1788885301):
        libc.srand(seed)
        values = bytes(libc.rand() & 255 for _ in range(1024))
        index = values.find(target)
        if index >= 0:
            matches.append({'seed': seed, 'output_index': index})
    report = {'initial_keys': [f'{key:08x}' for key in INITIAL],
              'entries': results, 'glibc_rand_header_matches': matches,
              'password_recovered': False}
    (HERE / 'zip_evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
