"""Recover fragmented archive pages using independently recovered ZIP directory.

Offline evidence parser only. Unknown bytes are tracked explicitly; only complete
entries with matching plaintext CRC and length are exported.
"""
from pathlib import Path
import json
import mmap
import struct
import subprocess
import zlib
from Crypto.Cipher import AES
from verify_zip_evidence import decrypt

HERE = Path(__file__).resolve().parent
WORDS = [x & 0xffffffff for x in [2032387434, 2144802918, 1612300407,
         -1744597057, 376328228, -333502917, 137095450, -350496053]]
KEY = struct.pack('>4I', *(WORDS[i] ^ WORDS[i + 4] for i in range(4)))
IV = int.from_bytes(struct.pack('>4I', WORDS[4], WORDS[5], 0, 0), 'big')


def crypt(data, offset):
    cipher = AES.new(KEY, AES.MODE_CTR, nonce=b'', initial_value=IV + offset // 16)
    cipher.encrypt(bytes(offset % 16))
    return cipher.encrypt(data)


def main():
    records = json.loads((HERE / 'archive_central_records.json').read_text())
    raw, known = bytearray(65408), bytearray(65408)
    pages = []
    signatures = {crypt(b'PK\x03\x04\x14\0', r['local_offset']) for r in records}
    pattern = '|'.join(''.join(f'\\x{b:02x}' for b in sig) for sig in signatures)
    scan = subprocess.run(['rg', '--text', '--json', '--multiline',
                           '--no-unicode', '--regexp', pattern,
                           str(HERE.parent / 'evidence/mem.clean')], capture_output=True)
    if scan.returncode not in (0, 1):
        raise RuntimeError(scan.stderr.decode(errors='replace'))
    hits = []
    for line in scan.stdout.splitlines():
        event = json.loads(line)
        if event['type'] == 'match':
            data = event['data']
            hits.extend(data['absolute_offset'] + sub['start'] for sub in data['submatches'])
    print('Candidate header positions:', len(hits), flush=True)
    with (HERE.parent / 'evidence/mem.clean').open('rb') as f, mmap.mmap(
            f.fileno(), 0, access=mmap.ACCESS_READ) as memory:
        segments, pos = [], 0
        while pos < len(memory):
            magic, version, start, end, reserved = struct.unpack_from('<IIQQQ', memory, pos)
            assert magic == 0x4c694d45
            segments.append((start, end + 1, pos + 32))
            pos += 32 + end - start + 1

        def save_page(hit, logical):
            for start, end, file_start in segments:
                if file_start <= hit < file_start + end - start:
                    within = (start + hit - file_start) % 4096
                    base, logical_base = hit - within, logical - within
                    lo, hi = max(logical_base, 0), min(logical_base + 4096, len(raw))
                    data = crypt(memory[base + lo - logical_base:base + hi - logical_base], lo)
                    for i, b in enumerate(data, lo):
                        assert not known[i] or raw[i] == b, 'Conflicting reconstructed bytes'
                    raw[lo:hi] = data
                    known[lo:hi] = b'\1' * (hi - lo)
                    pages.append({'memory': hex(base), 'logical': logical_base})
                    return
            raise ValueError('Hit outside LiME segments')

        eocd = bytes.fromhex('504b050600000000270027007f0b0000ebf300000000')
        assert crypt(memory[0x1cd8fbe:0x1cd8fbe + 22], 65386) == eocd
        save_page(0x1cd8fbe, 65386)
        for record in records:
            offset = record['local_offset']
            if all(known[offset:offset + 30]):
                continue
            signature = crypt(b'PK\x03\x04\x14\0', offset)
            found = False
            for hit in hits:
                if memory[hit:hit + len(signature)] != signature:
                    continue
                header = crypt(memory[hit:hit + 512], offset)
                h = struct.unpack_from('<4s5H3I2H', header)
                name = header[30:30 + h[9]].decode(errors='replace')
                if (name == record['name'] and h[6] == int(record['crc32'], 16)
                        and h[7] == record['compressed_size'] and h[8] == record['plain_size']):
                    save_page(hit, offset)
                    found = True
                    break
            print(record['name'], 'page recovered' if found else 'missing', flush=True)

    (HERE / 'archive_from_central.zip').write_bytes(raw)
    (HERE / 'archive_from_central_known.bin').write_bytes(known)
    output = HERE / 'decrypted_from_central'
    output.mkdir(exist_ok=True)
    results = []
    for index, record in enumerate(records):
        offset = record['local_offset']
        result = dict(record, complete=False)
        if all(known[offset:offset + 30]):
            h = struct.unpack_from('<4s5H3I2H', raw, offset)
            assert h[0] == b'PK\x03\x04'
            start = offset + 30 + h[9] + h[10]
            end = start + h[7]
            if end <= len(raw) and all(known[offset:end]):
                payload = decrypt(raw[start:end])[12:]
                if h[3] == 8:
                    payload = zlib.decompress(payload, -15)
                else:
                    assert h[3] == 0
                result.update(complete=True, crc_valid=zlib.crc32(payload) == h[6],
                              size_valid=len(payload) == h[8])
                assert result['crc_valid'] and result['size_valid']
                (output / f'{index:02d}_{Path(record["name"]).name}').write_bytes(payload)
        results.append(result)
    report = {'known_bytes': sum(known), 'total_bytes': len(raw), 'pages': pages,
              'verified_entries': sum(r['complete'] for r in results), 'entries': results}
    (HERE / 'archive_central_recovery.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('known_bytes', 'total_bytes', 'verified_entries')}))


if __name__ == '__main__':
    main()
